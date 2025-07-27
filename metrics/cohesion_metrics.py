import json
import re
import numpy as np
from sql_metadata import Parser

class CohesionEvaluator:
    """
    Calculates five session cohesion metrics based on the sequence of queries
    actually chosen by the user.
    """

    def __init__(self, json_filepath):
        self.chosen_queries_sql = self._parse_log_file_for_chosen_queries(json_filepath)
        self.parsed_chosen_queries = [self._parse_sql_for_fragments(sql) for sql in self.chosen_queries_sql]

    def _parse_log_file_for_chosen_queries(self, filepath):
        """Reads the sequence of queries actually chosen by the user."""
        with open(filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        return [step.get('SQL', {}).get('sql') for step in log_data['userdata']['suerQueryData']]

    def _parse_sql_for_fragments(self, sql):
        """Parses the SQL statement into fragments: projections, selections, aggregations, tables."""
        if not sql: return {'projections': set(), 'selections': set(), 'aggregations': set(), 'tables': set()}
        try:
            AGG_OPS = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
            aggs = {op for op in AGG_OPS if re.search(r'\b' + op + r'\s*\(', sql, re.IGNORECASE)}
            selections = set()
            where_match = re.search(r'WHERE\s+(.*?)(?:GROUP BY|ORDER BY|LIMIT|;|\Z)', sql, re.IGNORECASE | re.DOTALL)
            if where_match:
                conditions = where_match.group(1)
                selections = {cond.strip() for cond in re.split(r'\bAND\b|\bOR\b', conditions, flags=re.IGNORECASE)}
            parser = Parser(sql)
            return {'projections': set(parser.columns), 'selections': selections, 'aggregations': aggs,
                    'tables': set(parser.tables)}
        except Exception:
            return {'projections': set(), 'selections': set(), 'aggregations': set(), 'tables': set()}

    def evaluate(self):
        """Calculates and returns the cohesion metrics."""
        if len(self.parsed_chosen_queries) < 2:
            return {"Edit Index": 0, "Jaccard Index": 0, "Cosine Index": 0,
                    "Common Fragments Index": 0, "Common Tables Index": 0}

        indices = {k: [] for k in ["edit", "jaccard", "cosine", "cf", "ct"]}
        max_tables_in_session = max((len(p['tables']) for p in self.parsed_chosen_queries if p['tables']), default=1)

        for i in range(1, len(self.parsed_chosen_queries)):
            q_prev, q_curr = self.parsed_chosen_queries[i - 1], self.parsed_chosen_queries[i]

            # Edit Index
            added = sum(len(q_curr[key] - q_prev[key]) for key in q_curr)
            removed = sum(len(q_prev[key] - q_curr[key]) for key in q_curr)
            indices["edit"].append(max(0, 1 - ((added + removed) / 10)))

            # Jaccard Index
            fragments_prev = q_prev['projections'] | q_prev['selections'] | q_prev['aggregations'] | q_prev['tables']
            fragments_curr = q_curr['projections'] | q_curr['selections'] | q_curr['aggregations'] | q_curr['tables']
            intersection_size = len(fragments_prev.intersection(fragments_curr))
            union_size = len(fragments_prev.union(fragments_curr))
            indices["jaccard"].append(intersection_size / union_size if union_size > 0 else 0)

            # Cosine Index
            vec_prev = np.array([len(q_prev[f]) for f in ['projections', 'selections', 'aggregations', 'tables']])
            vec_curr = np.array([len(q_curr[f]) for f in ['projections', 'selections', 'aggregations', 'tables']])
            dot_product, norm_prev, norm_curr = np.dot(vec_prev, vec_curr), np.linalg.norm(vec_prev), np.linalg.norm(
                vec_curr)
            indices["cosine"].append(dot_product / (norm_prev * norm_curr) if norm_prev > 0 and norm_curr > 0 else (
                1.0 if norm_prev == norm_curr else 0.0))

            # Common Fragments Index
            ncf = sum(len(q_curr[key].intersection(q_prev[key])) for key in q_curr)
            indices["cf"].append(min(1, ncf / 10))

            # Common Tables Index
            nct = len(q_curr['tables'].intersection(q_prev['tables']))
            indices["ct"].append(nct / max_tables_in_session if max_tables_in_session > 0 else 0)

        return {
            "Edit Index": np.mean(indices["edit"]),
            "Jaccard Index": np.mean(indices["jaccard"]),
            "Cosine Index": np.mean(indices["cosine"]),
            "Common Fragments Index": np.mean(indices["cf"]),
            "Common Tables Index": np.mean(indices["ct"])
        }