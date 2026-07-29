import re,sqlglot,logging
logger = logging.getLogger()
from llm_db.config import SQL_TYPES
from datetime import datetime



def get_insert_columns(sql: str) -> list[str]:
    """
    Extract columns from an INSERT statement.

    Example:
        INSERT INTO patient (nom, prenom)
        VALUES ('Lucas', 'Emma')

    Returns:
        ["nom", "prenom"]
    """
    try:
        tree = sqlglot.parse_one(sql, read="postgres")

        if not isinstance(tree, sqlglot.exp.Insert):
            return []

        columns = tree.find(sqlglot.exp.Schema)

        if not columns:
            return []

        return [
            column.name
            for column in columns.expressions
            if isinstance(column, sqlglot.exp.Identifier)
        ]

    except Exception:
        return []


def get_table_name(sql: str) -> str | None:
    """
    Extract the table name from any SQL query.

    Example:
        INSERT INTO public.patient (...)
        -> patient
    """
    try:
        tree = sqlglot.parse_one(sql, read="postgres")

        table = tree.find(sqlglot.exp.Table)

        if not table:
            return None

        return table.name

    except Exception:
        return None


def detect_sql_type(sql: str) -> str | None:
    """
    Detect SQL operation type.

    Returns:
        SELECT / INSERT / UPDATE / DELETE / None
    """
    try:
        tree = sqlglot.parse_one(sql, read="postgres")

        if isinstance(tree, sqlglot.exp.Select):
            return "SELECT"

        if isinstance(tree, sqlglot.exp.Insert):
            return "INSERT"

        if isinstance(tree, sqlglot.exp.Update):
            return "UPDATE"

        if isinstance(tree, sqlglot.exp.Delete):
            return "DELETE"

        return None

    except Exception:
        logger.debug(sql)
        return None

import re


import re


import re


def extract_insertion_fields(
    sql_query: str,
    previous_inserted_fields: dict[str, str] | None = None
) -> dict[str, str]:
    """
    Extract INSERT columns/values and merge with previous fields.

    Previous fields always have priority.
    Existing fields are never overwritten.
    """

    if previous_inserted_fields is None:
        previous_inserted_fields = {}

    # Extract columns only
    column_pattern = r"""
        INSERT\s+INTO\s+\w+\s*
        \((.*?)\)
        \s*VALUES
    """

    match = re.search(
        column_pattern,
        sql_query,
        re.IGNORECASE | re.VERBOSE | re.DOTALL
    )

    if not match:
        return previous_inserted_fields

    columns_raw = match.group(1)

    columns = [
        c.strip()
        for c in columns_raw.split(",")
    ]

    # Extract everything after VALUES(
    values_start = match.end()

    values_raw = sql_query[values_start:].strip()

    # Remove surrounding VALUES parentheses
    if values_raw.startswith("("):
        values_raw = values_raw[1:]

    if values_raw.endswith(";"):
        values_raw = values_raw[:-1]

    if values_raw.endswith(")"):
        values_raw = values_raw[:-1]


    # Split values safely
    values = []
    current = ""
    depth = 0
    in_quotes = False

    i = 0

    while i < len(values_raw):
        char = values_raw[i]

        if char == "'":
            in_quotes = not in_quotes

        elif not in_quotes:
            if char == "(":
                depth += 1

            elif char == ")":
                depth -= 1

            elif char == "," and depth == 0:
                values.append(current.strip())
                current = ""
                i += 1
                continue

        current += char
        i += 1

    if current.strip():
        values.append(current.strip())


    new_fields = dict(zip(columns, values))


    # Previous fields are immutable
    merged = new_fields.copy()

    for key, value in previous_inserted_fields.items():
        merged[key] = value

    return merged



def _extract_table_from_foreign_key(error_msg: str) -> str:
    """Extract the dependent table name from a foreign key error message"""
    
    patterns = [ r'constraint\s+"[^"]+"\s+on\s+table\s+"([^"]+)"', r'references\s+table\s+"([^"]+)"', r'referenced\s+from\s+table\s+"([^"]+)"', r'on\s+table\s+"([^"]+)"\s*$']
    
    for pattern in patterns:
        match = re.search(pattern, error_msg, re.IGNORECASE)
        if match:
            return match.group(1)
        
    all_tables = re.findall(r'table\s+"([^"]+)"', error_msg, re.IGNORECASE)
    if all_tables:
        return all_tables[-1]  # Return the last table mentioned
    
    return "unknown"


def normalize_insert_nulls(sql: str) -> str:
    """
    Remove NULL columns from INSERT statements.

    Example:
        INSERT INTO acte_medecin(acte, duree, prix, id_medecin)
        VALUES('radiographie', NULL, NULL, 1);

    becomes:

        INSERT INTO acte_medecin(acte, id_medecin)
        VALUES('radiographie', 1);
    """

    try:
        tree = sqlglot.parse_one(sql, read="postgres")

        if not isinstance(tree, sqlglot.exp.Insert):
            return sql

        schema = tree.find(sqlglot.exp.Schema)

        if not schema:
            return sql

        values = tree.find(sqlglot.exp.Values)

        if not values:
            return sql

        columns = schema.expressions
        row = values.expressions[0]

        new_columns = []
        new_values = []

        for column, value in zip(columns, row.expressions):

            # remove column/value pair
            if isinstance(value, sqlglot.exp.Null):
                continue

            new_columns.append(column)
            new_values.append(value)

        schema.set(
            "expressions",
            new_columns
        )

        row.set(
            "expressions",
            new_values
        )

        return tree.sql(dialect="postgres")

    except Exception as e:
        logger.debug(f"NULL normalization skipped: {e}")
        return sql

def _clean_sql_response(response: str) -> str:
    response = re.sub(r'```sql\n?', '', response)
    response = re.sub(r'```\n?', '', response)
    response = re.sub(r'^sql\n?', '', response, flags=re.IGNORECASE)
    
    lines = response.split('\n')
    clean_lines = []
    for line in lines:
        if not line.strip().startswith('--'):
            clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


def normalize_name_search(sql: str) -> str:
    """
    Normalize patient name searches.

    Converts:
        nom = 'Lucas'
        prenom = 'Lucas'
        nom ILIKE '%Lucas%'

    into:

        (nom ILIKE '%Lucas%' OR prenom ILIKE '%Lucas%')

    If SQL parsing/transformation fails, returns the original SQL.
    """

    try:
        tree = sqlglot.parse_one(sql, read="postgres")

        comparison_types = (
            sqlglot.exp.EQ,
            sqlglot.exp.Like,
            sqlglot.exp.ILike,
        )

        def transform(node):
            if not isinstance(node, comparison_types):
                return node

            column = node.this

            if not isinstance(column, sqlglot.exp.Column):
                return node

            if column.name.lower() not in {"nom", "prenom"}:
                return node

            value = node.expression.copy()

            # nom = 'Lucas'
            # becomes '%Lucas%'
            if isinstance(node, sqlglot.exp.EQ):
                if isinstance(value, sqlglot.exp.Literal):
                    value = sqlglot.exp.Literal.string(
                        f"%{value.this}%"
                    )

            return sqlglot.exp.Paren(
                this=sqlglot.exp.Or(
                    this=sqlglot.exp.ILike(
                        this=sqlglot.exp.Column(
                            this=sqlglot.exp.Identifier(this="nom")
                        ),
                        expression=value.copy(),
                    ),
                    expression=sqlglot.exp.ILike(
                        this=sqlglot.exp.Column(
                            this=sqlglot.exp.Identifier(this="prenom")
                        ),
                        expression=value,
                    ),
                )
            )

        tree = tree.transform(transform)

        return tree.sql(dialect="postgres")

    except Exception as e:
        logger.debug(f"Name normalization skipped: {e}")
        return sql


def normalize_date_literals(sql: str, user_query: str) -> str:
    """
    Normalize hallucinated years only for INSERT statements containing date_rdv.

    Rules:
    - If user explicitly gave a year -> keep it.
    - If INSERT does not contain date_rdv -> do nothing.
    - If date_rdv exists and user gave no year -> replace generated year with current year.
    """
    print(f"first arg = {sql}\nsecond_arg : {user_query}")

    current_year = datetime.now().year

    # Only apply to queries inserting date_rdv
    if not re.search(r"\bdate_rdv\b", sql, re.IGNORECASE):
        return sql

    # User explicitly mentioned a year
    if re.search(r"\b20\d{2}\b", user_query):
        return sql

    pattern = r"(\d{4})-(\d{2})-(\d{2})([^']*)"

    def replace(match):
        _, month, day, rest = match.groups()
        return f"'{current_year}-{month}-{day}{rest}'"

    return re.sub(pattern, replace, sql)



def normalize(sql: str , user_query : str) -> str:
    """
    Global SQL normalization pipeline.
    """
    lower_sql = sql.lower()

    if "nom ilike" in lower_sql and "prenom ilike" in lower_sql:
        return sql #cuz otherwise this function aint gonna be idempotent + cant track whether i called it twice or not (too lazy)
    
    sql = normalize_insert_nulls(sql)
    sql = normalize_name_search(sql)
    sql = normalize_date_literals(sql, user_query)

    return sql






