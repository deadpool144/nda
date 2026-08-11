import difflib

class ComparisonPipeline:
    def compare(self, text_v1: str, text_v2: str) -> dict:
        """
        Generates a diff of the two texts.
        Returns basic statistics about changes.
        """
        d = difflib.Differ()
        diff = list(d.compare(text_v1.splitlines(), text_v2.splitlines()))
        
        additions = sum(1 for line in diff if line.startswith('+ '))
        deletions = sum(1 for line in diff if line.startswith('- '))
        
        return {
            "lines_added": additions,
            "lines_removed": deletions,
            "total_changes": additions + deletions
        }
