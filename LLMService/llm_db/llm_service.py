import ollama,re,time, psycopg2, os, logging, json
from dotenv import load_dotenv
from llm_db.config import REQUIRED_FIELDS
from llm_db.session import DatabaseSession, SessionManager
load_dotenv()
import llm_db.sql_tools as sql_tools
from psycopg2.extras import RealDictCursor
logger = logging.getLogger()

# What we call from here is "generate_and_execute"

def timecalculation(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"⏱️  {func.__name__} a pris {end_time - start_time:.2f} secondes")
        return result
    return wrapper



class SQLGenerator:
    MODEL_NAME = "qwen2.5-coder:3b"
    MAX_RETRIES = 5
    
    @staticmethod
    def _get_system_prompt(id_medecin: int , domain : str = "system") -> str:
        assert domain in ["acte_medecin", "appointments" ,"doctor_notes", "patients" , "system"]
        with open(f"llm_db/prompts/{domain}_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().replace("[id_medecin]", str(id_medecin))


    @staticmethod
    def load_session_history(session : DatabaseSession) -> str:
        return f"""
            VOUS DEVEZ INSERER CES CHAMPS DANS VOTRE REQUETE :
            {session.clarification_history}
        """ if session.clarification_history else ""
    


    @staticmethod
    def _validate_doctor_id(sql_query: str, id_medecin: int) -> bool:
        sql = " ".join(sql_query.split()).lower()

        doctor_id = str(id_medecin)

        # Case 1: WHERE id_medecin = X
        where_pattern = rf"\bid_medecin\b\s*=\s*{re.escape(doctor_id)}\b"

        if re.search(where_pattern, sql):
            return True

        # Case 2: INSERT containing id_medecin column and value
        insert_pattern = (
            rf"insert\s+into\s+\w+\s*"
            rf"\([^)]*\bid_medecin\b[^)]*\)"
            rf"\s*values\s*\([^)]*\b{re.escape(doctor_id)}\b[^)]*\)"
        )

        if re.search(insert_pattern, sql):
            return True

        return False
        
    @staticmethod
    def _build_correction_prompt(user_query: str, id_medecin: int) -> str:
        system_prompt = SQLGenerator._get_system_prompt(id_medecin)
        with open("llm_db/prompts/correction_prompt.txt","r") as f:
            correction_prompt = f.read().replace("[id_medecin]", str(id_medecin)).replace("[user_query]",user_query)
        return f"{system_prompt}\n\n{correction_prompt}"


    
    @staticmethod
    def generate_sql(user_query: str, session: DatabaseSession, domain : str , custom_system_prompt: str = None) -> str:
        if session.id_medecin is None:
            raise ValueError("id_medecin est OBLIGATOIRE")
        
        system_prompt = custom_system_prompt if custom_system_prompt else SQLGenerator._get_system_prompt(session.id_medecin , domain)

        system_prompt += SQLGenerator.load_session_history(session)
        
        full_prompt = f"{system_prompt}\n\nUtilisateur (medecin_id = {session.id_medecin}): {user_query}\n\nSQL:"
        for attempt in range(SQLGenerator.MAX_RETRIES):
            sql_query = ollama.chat(
                model=SQLGenerator.MODEL_NAME,
                messages=[{"role": "user", "content": full_prompt}],
                options={
                                    "num_ctx": 2048,
                                    "temperature": 0,
                                    "num_gpu": 999
                                }
            )['message']['content'].strip()
            print(f"before normalize = {sql_query}")
            sql_query = sql_tools.normalize(sql_tools._clean_sql_response(sql_query), user_query)
            print(f"after normalize = {sql_query}")
            
            if SQLGenerator._validate_doctor_id(sql_query, session.id_medecin):
                return sql_query
            
            full_prompt = SQLGenerator._build_correction_prompt(user_query, session.id_medecin)
            print(f"attempt {attempt}\nTHE MODEL GOT THE QUERY WRONG : {sql_query}")
        
        raise RuntimeError(f"Impossible de générer une requête valide avec id_medecin = {session.id_medecin} après {SQLGenerator.MAX_RETRIES} tentatives")


    
    @staticmethod
    def execute_sql(sql_query: str) -> str:
        """
        Execute a SQL query and return results as formatted string
        """
        logger.critical(f"sql = {sql_query}")

        dsn = os.environ.get("DB_DSN")
        if not dsn:
            raise ValueError("DB_DSN environment variable is not set")
        
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(dsn)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql_query)
            
            # Check if it's a SELECT query
            if sql_query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                if not rows:
                    return "No results found."
                
                # Format as a nice table
                if len(rows) == 1:
                    return "\n".join([f"{k}: {v}" for k, v in rows[0].items()])
                else:
                    result_lines = []
                    for i, row in enumerate(rows, 1):
                        result_lines.append(f"Enregistrement {i}:" + "\n")
                        for k, v in row.items():
                            result_lines.append(f"  {k}: {v}")
                        result_lines.append("\n")  # Ligne vide entre les enregistrements
                    return "\n".join(result_lines)
            else:
                # INSERT, UPDATE, DELETE - commit and return row count
                conn.commit()
                row_count = cursor.rowcount
                return f"C'est fait ! J'ai modifié {row_count} ligne(s) pour vous."
                
        except Exception as e:
            if conn:
                conn.rollback()
            return f"Error executing query: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    @timecalculation
    def generate_and_execute(
        user_query: str,
        session: DatabaseSession,
        domain : str = "system"
    ) -> str:

        assert isinstance(user_query, str), "user_query must be a string"
        assert isinstance(session, DatabaseSession), "session must be DatabaseSession"

        # Handle ongoing workflows first
        if session.status == "WAITING_CONFIRMATION" and session.query_type == "DELETE":
            return SQLGenerator.handle_delete_confirmation(user_query, session)

        if session.status == "WAITING_MISSING_FIELDS" and session.query_type == "INSERT":
            return SQLGenerator.handle_missing_insert_fields(user_query, session , domain)

        return SQLGenerator.generate_execute_with_retry(
            user_query,
            session,
            domain
        )


    @staticmethod
    def handle_delete_confirmation(
        user_query: str,
        session: DatabaseSession
    ) -> str:

        words = user_query.lower().split()

        if any(w in words for w in ("yes", "oui", "ok", "confirm")):

            result = SQLGenerator.execute_sql(session.generated_sql)

            if "foreign key" in result.lower():
                table_name = sql_tools._extract_table_from_foreign_key(result)

                SessionManager.delete_session(
                    session.id_medecin,
                    session.id_session
                )

                return (
                    f"Impossible de supprimer : cet enregistrement "
                    f"est référencé dans la table '{table_name}'. "
                    f"Supprimez d'abord les références."
                )

            SessionManager.delete_session(
                session.id_medecin,
                session.id_session
            )

            return f"✅ {result}"


        if any(w in words for w in ("non", "no", "annule")):

            SessionManager.delete_session(
                session.id_medecin,
                session.id_session
            )

            return "Suppression annulée."


        return (
            "Je n'ai pas compris. Voulez-vous confirmer la suppression ?\n\n"
            f"{session.preview_result}\n\n"
            "Répondez 'oui' ou 'non'."
        )


    @staticmethod
    def handle_missing_insert_fields(
        user_query: str,
        session: DatabaseSession,
        domain : str
    ) -> str:

        missing_fields_str = ", ".join(
            session.missing_fields
        ).replace("_", " ")

        

        prompt = f"""
    {SQLGenerator._get_system_prompt(session.id_medecin , domain)}

    CONTEXTE:
    Vous êtes en train de compléter une opération d'insertion
    de données commencée précédemment.

    Cette session correspond à une seule opération SQL.
    Toutes les informations fournies par l'utilisateur depuis le début
    de cette opération sont importantes.

    Historique complet de l'opération:
    {session.clarification_history}

    Champs encore manquants:
    {missing_fields_str}

    Votre tâche:
    - Utilisez toutes les informations de l'historique.
    - Complétez tous les champs nécessaires si l'utilisateur les mentionne, il ne faut rien inventer du tout !
    - Générez une requête INSERT complète.

    """

        raw_sql = SQLGenerator.generate_sql(
            user_query,
            session,
            domain,
            custom_system_prompt=prompt
        )

        print(f"before normalize = {raw_sql}")
        sql_query = sql_tools.normalize(sql_tools._clean_sql_response(raw_sql) , user_query)
        print(f"after normalize = {sql_query}")

        missing_fields = SQLGenerator.validate_insertion_missing_fields(
            sql_query
        )

        if missing_fields:

            session.missing_fields = list(missing_fields)
            session.clarification_history = json.dumps(sql_tools.extract_insertion_fields(sql_query))

            SessionManager.save_session(session)

            return (
                "J'aurai encore besoin des informations suivantes : "
                + ", ".join(missing_fields).replace("_", " ")
            )

        result = SQLGenerator.execute_sql(sql_query)

        if not result.startswith("Error executing query:"):

            SessionManager.delete_session(
                session.id_medecin,
                session.id_session
            )

            return result


        session.set_status("FRESH")
        session.query_type = None

        SessionManager.save_session(session)

        return f"Erreur lors de l'insertion"

    @staticmethod
    def handle_delete(sql_query: str, session: DatabaseSession) -> str:
        """Handle DELETE operations with preview and confirmation"""
        # Convert DELETE to SELECT to preview what will be deleted
        preview_query = re.sub(r'^DELETE\s+FROM', 'SELECT * FROM', sql_query, flags=re.IGNORECASE)
        
        # If the DELETE has a subquery, we need to handle it differently
        if "LIMIT 1" in sql_query:
            # For targeted deletes (one row), we can preview
            preview_result = SQLGenerator.execute_sql(preview_query)
        else:
            # For bulk deletes, we need to be more careful
            # Add LIMIT 5 to preview a few rows
            if "LIMIT" not in preview_query.upper():
                preview_query = preview_query.rstrip(";") + " LIMIT 5;"
            preview_result = SQLGenerator.execute_sql(preview_query)
        
        if "No results found" in preview_result:
            return "Aucun enregistrement trouvé à supprimer."
        
        # Store the DELETE query and preview in session
        session.set_status("WAITING_CONFIRMATION")
        session.query_type = "DELETE"
        session.generated_sql = sql_query
        session.preview_result = preview_result
        SessionManager.save_session(session)
        
        return f"Êtes-vous sûr de vouloir supprimer ces enregistrements ?\n\n{preview_result}\n\nConfirmer avec 'oui' ou annuler avec 'non'."

    @staticmethod
    def validate_insertion_missing_fields(sql_query: str) -> list[str]:

        table_name = sql_tools.get_table_name(sql_query)

        if table_name is None:
            return []

        required_fields = REQUIRED_FIELDS.get(table_name)

        if required_fields is None:
            return []

        insert_columns = sql_tools.get_insert_columns(sql_query)
        print(f"required_fields = {required_fields}\ninsert_columns = {insert_columns}\nthe query : {sql_query}")

        if not insert_columns:
            return []

        return list(set(required_fields) - set(insert_columns))
                
    @staticmethod
    def generate_execute_with_retry(
        user_query: str,
        session: DatabaseSession,
        domain : str
    ):

        error_context = None

        for attempt in range(SQLGenerator.MAX_RETRIES + 1):

            raw_sql = SQLGenerator.generate_sql(
                user_query,
                session,
                domain,
                custom_system_prompt=error_context
            )

            try:
                print(f"before normalize = {raw_sql}")
                sql_query = sql_tools.normalize(sql_tools._clean_sql_response(raw_sql) , user_query)
                print(f"after normalize = {sql_query}")

            except Exception as e:
                print(f"SQL normalization failed: {e}")
                sql_query = raw_sql
            print(f"sql = {sql_query}")
            operation = sql_tools.detect_sql_type(sql_query)

            if operation is None:
                SessionManager.delete_session(session.id_medecin , session.id_session)
                return "No SQL operation detected"


            if operation == "INSERT":

                missing_fields = SQLGenerator.validate_insertion_missing_fields(
                    sql_query
                )

                if missing_fields:

                    session.set_status("WAITING_MISSING_FIELDS")
                    session.query_type = "INSERT"
                    session.missing_fields = list(missing_fields)

                    session.clarification_history = sql_tools.extract_insertion_fields(sql_query)

                    SessionManager.save_session(session)

                    return (
                        "Veuillez fournir les informations suivantes s'il vous plaît : "
                        + ", ".join(missing_fields).replace("_", " ")
                    )


            if operation == "DELETE":
                return SQLGenerator.handle_delete(
                    sql_query,
                    session
                )

            result = SQLGenerator.execute_sql(sql_query)


            if not result.startswith("Error executing query:"):

                SessionManager.delete_session(
                    session.id_medecin,
                    session.id_session
                )

                return result


            if attempt == SQLGenerator.MAX_RETRIES:
                SessionManager.delete_session(
                                    session.id_medecin,
                                    session.id_session
                                )
                raise RuntimeError(
                    f"Failed after {SQLGenerator.MAX_RETRIES + 1} attempts.\n"
                    f"Last error: {result}"
                )


            if "foreign key" in result.lower():
                return result

            error_context = f"""
                {SQLGenerator._get_system_prompt(session.id_medecin, domain)}

                {f"ERREUR DE LA REQUETE SQL FOURNIE\n" + result}

                Original request:
                {user_query}

                GENERATE A COMPLETELY DIFFERENT SQL QUERY.
                Do NOT repeat the same error.
                Return ONLY SQL.
            """

            print(f"🔄 Retry {attempt + 1}: Injecting error...")


        raise RuntimeError("Unexpected retry termination")




if __name__ == "__main__":
    ollama.generate(
        model="qwen2.5-coder:3b",
        prompt="",
        keep_alive="1h",
        options = {"num_gpu" : 999, "temperature" : 0 , "num_predict" : 1 , "num_ctx": 2048}
    )
    SessionManager.delete_session(1,1)
    print("app started")
    print("=" * 50)
    while 1 :
        query1 = input("QUERY= ")
        id_medecin = int(input("Enter id_medecin = "))
        id_session = int(input("Enter id_session = "))
        domain = input("Enter domaine = ")
        session = SessionManager.get_session(id_medecin , id_session)
        print(session)
        print(session,flush = True)
        result1 = SQLGenerator.generate_and_execute(query1, session , domain)
        print(f"result:\n{result1}\n")
    
