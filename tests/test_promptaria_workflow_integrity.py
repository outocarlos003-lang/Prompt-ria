"""Static safeguards for privileged pull-request integration workflows."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "promptaria-integracao-pr.yml"
AUTO_MERGE = ROOT / ".github" / "workflows" / "promptaria-auto-merge.yml"
TEST_WORKFLOW = ROOT / ".github" / "workflows" / "promptaria-tests.yml"


class PullRequestIntegrationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")
        cls.auto_merge_source = AUTO_MERGE.read_text(encoding="utf-8")
        cls.test_workflow_source = TEST_WORKFLOW.read_text(encoding="utf-8")

    def test_comment_only_prepares_pr_and_never_bypasses_checks(self):
        self.assertIn("github.event.comment.author_association == 'OWNER'", self.source)
        self.assertIn("startsWith(github.event.comment.body, '/promptaria merge ')", self.source)
        self.assertIn('expected="/promptaria merge $head_sha"', self.source)
        self.assertIn('if [[ "$COMMENT_BODY" != "$expected" ]]; then', self.source)
        self.assertIn('base="$(jq -r \'.base.ref\' <<< "$pr")"', self.source)
        self.assertIn('head_repo="$(jq -r \'.head.repo.full_name // ""\' <<< "$pr")"', self.source)
        self.assertIn('if [[ "$base" != "main" || "$head_repo" != "$REPOSITORY" || "$state" != "open" ]]; then', self.source)
        self.assertIn('gh pr ready "$PR_NUMBER" --repo "$REPOSITORY"', self.source)
        self.assertNotIn("gh pr merge", self.source)

    def test_auto_merge_requires_explicit_owner_approval_for_exact_tested_sha(self):
        self.assertIn('workflows: ["Promptária PR Checks",', self.auto_merge_source)
        self.assertIn('commits/$TESTED_SHA/check-runs?per_page=100', self.auto_merge_source)
        self.assertIn('returned_checks="$(jq \'.check_runs | length\' <<< "$checks")"', self.auto_merge_source)
        self.assertIn('"$returned_checks" -ne "$total_checks"', self.auto_merge_source)
        self.assertIn('select(.status != "completed")', self.auto_merge_source)
        self.assertIn('select(.status == "completed" and .conclusion != "success"', self.auto_merge_source)
        self.assertIn('if [[ "$state" != "open" || "$base" != "main" || "$head_repo" != "$GH_REPO" || "$draft" != "false" ]]; then', self.auto_merge_source)
        self.assertIn('expected_approval="/promptaria merge $TESTED_SHA"', self.auto_merge_source)
        self.assertIn('author_association == "OWNER"', self.auto_merge_source)
        self.assertIn('Missing explicit OWNER approval for this exact tested SHA', self.auto_merge_source)
        self.assertIn('head_sha" != "$TESTED_SHA"', self.auto_merge_source)
        self.assertIn('current" != "$TESTED_SHA"', self.auto_merge_source)
        self.assertIn('--match-head-commit "$TESTED_SHA"', self.auto_merge_source)
        self.assertIn("--squash", self.auto_merge_source)

    def test_checks_run_when_a_draft_is_marked_ready(self):
        self.assertIn("types: [opened, synchronize, reopened, ready_for_review]", self.test_workflow_source)

    def test_privileged_workflows_use_explicit_minimum_permissions(self):
        self.assertIn("contents: read", self.source)
        self.assertIn("pull-requests: write", self.source)
        self.assertIn("contents: write", self.auto_merge_source)
        self.assertIn("pull-requests: write", self.auto_merge_source)
        self.assertIn("issues: read", self.auto_merge_source)


if __name__ == "__main__":
    unittest.main()
