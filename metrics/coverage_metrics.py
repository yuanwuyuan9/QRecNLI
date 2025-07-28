import json
import re
from sql_metadata import Parser

class CoverageAndNoveltyEvaluator:
    """
    Calculates coverage and novelty related metrics:
    1. Schema Exploration Breadth (Table/Column Coverage)
    2. Operator Diversity (Aggregation/Clause Coverage)
    This considers all recommended queries. For instance, if 5 queries are
    recommended in one round, all are included, not just the one the user clicked on.
    """

    def __init__(self, json_filepath, schema_filepath):
        # Reads the initial recommended queries and all subsequent ones.
        self.recommendation_lists_sql = self._parse_log_file_for_recommendations(json_filepath)
        self.schema_info = self._parse_schema(schema_filepath)
        self.parsed_recommendations = [[self._parse_sql(sql) for sql in step_sqls] for step_sqls in
                                       self.recommendation_lists_sql]

    def _parse_log_file_for_recommendations(self, filepath):
        """Reads the initial recommended queries and all subsequent ones from the log file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        recommendation_lists = [log_data['userdata']['origQuerySugg']['sql']]
        for step in log_data['userdata']['suerQueryData']:
            if 'QuerySugg' in step and 'sql' in step['QuerySugg']:
                recommendation_lists.append(step['QuerySugg']['sql'])
        return recommendation_lists

    def _parse_schema(self, filepath):
        """Reads the corresponding database information from schema.sql."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tables = re.findall(r'CREATE TABLE\s+([\w`"]+)', content, re.IGNORECASE)
            table_defs = re.findall(r'CREATE TABLE\s+[\w`"]+\s*\((.*?)\);', content, re.DOTALL | re.IGNORECASE)
            all_columns = set()
            for table_def in table_defs:
                for line in table_def.strip().split('\n'):
                    line = line.strip()
                    if not line or line.upper().startswith(('PRIMARY', 'FOREIGN', 'CONSTRAINT', ')', 'UNIQUE')):
                        continue
                    match = re.match(r'[`"]?(\w+)[`"]?', line)
                    if match:
                        all_columns.add(match.group(1))
            return {"tables": {t.strip('`"') for t in tables}, "columns": all_columns}
        except FileNotFoundError:
            print(f"Warning: Schema file '{filepath}' not found.")
            return {"tables": set(), "columns": set()}

    def _parse_sql(self, sql):
        """Parses a single SQL query to extract its components."""
        if not sql: return {'tables': set(), 'columns': set(), 'aggregations': set(), 'clauses': set()}
        try:
            AGG_OPS, CLAUSE_KEYWORDS = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'], {'GROUP BY', 'ORDER BY', 'JOIN'}
            aggs, clauses = set(), set()
            for op in AGG_OPS:
                if re.search(r'\b' + op + r'\s*\(', sql, re.IGNORECASE): aggs.add(op)
            for clause in CLAUSE_KEYWORDS:
                if re.search(r'\b' + clause + r'\b', sql, re.IGNORECASE): clauses.add(clause)
            parser = Parser(sql)
            return {'tables': set(parser.tables), 'columns': set(parser.columns), 'aggregations': aggs,
                    'clauses': clauses}
        except Exception:
            return {'tables': set(), 'columns': set(), 'aggregations': set(), 'clauses': set()}

    def calculate_coverage_metrics(self):
        """Calculates and returns the coverage metrics."""
        recommended_tables, recommended_columns, recommended_aggs, recommended_clauses = set(), set(), set(), set()
        for step_parsed in self.parsed_recommendations:
            for parsed_info in step_parsed:
                recommended_tables.update(parsed_info['tables'])
                recommended_columns.update(parsed_info['columns'])
                recommended_aggs.update(parsed_info['aggregations'])
                recommended_clauses.update(parsed_info['clauses'])

        total_tables, total_columns = self.schema_info['tables'], self.schema_info['columns']
        table_coverage = len(recommended_tables) / len(total_tables) if total_tables else 0
        column_coverage = len(recommended_columns) / len(total_columns) if total_columns else 0

        AGG_FUNCTIONS, CLAUSES = {'COUNT', 'SUM', 'AVG', 'MAX', 'MIN'}, {'GROUP BY', 'ORDER BY', 'JOIN'}
        agg_coverage = len(recommended_aggs.intersection(AGG_FUNCTIONS)) / len(AGG_FUNCTIONS) if AGG_FUNCTIONS else 0
        clause_coverage = len(recommended_clauses.intersection(CLAUSES)) / len(CLAUSES) if CLAUSES else 0

        return {
            "Table Coverage": table_coverage,
            "Column Coverage": column_coverage,
            "Aggregation Coverage": agg_coverage,
            "Clause Coverage": clause_coverage
        }

    def evaluate(self):
        """Runs the evaluation process."""
        return self.calculate_coverage_metrics()