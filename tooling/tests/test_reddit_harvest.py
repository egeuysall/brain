import unittest

from tooling.scripts.reddit_harvest import (
    extract_op_body_from_post_html,
    extract_posts_from_new_html,
    score_candidate,
)


class RedditHarvestParsingTests(unittest.TestCase):
    def test_extract_posts_from_new_html(self) -> None:
        html = """
        <div id="siteTable" class="sitetable linklisting">
          <div class=" thing id-t3_abc" data-subreddit="EngineeringManagers" data-permalink="/r/EngineeringManagers/comments/abc/test/">
            <p class="title"><a class="title may-blank" href="/r/EngineeringManagers/comments/abc/test/">Team context keeps getting lost</a></p>
            <p class="tagline ">submitted <time datetime="2026-03-21T10:00:00+00:00" class="live-timestamp">2 days ago</time> by <a class="author" href="/u/test">test_author</a></p>
          </div>
        </div>
        """
        posts = extract_posts_from_new_html(html, subreddit_hint="EngineeringManagers")
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["subreddit"], "EngineeringManagers")
        self.assertEqual(posts[0]["title"], "Team context keeps getting lost")
        self.assertTrue(posts[0]["url"].startswith("https://www.reddit.com/r/EngineeringManagers/comments/abc/test/"))
        self.assertEqual(posts[0]["author"], "test_author")

    def test_extract_op_body_from_post_html(self) -> None:
        html = """
        <div class=" thing id-t3_abc">
          <div class="entry">
            <div class="usertext-body may-blank-within md-container">
              <div class="md"><p>We keep finding blockers too late in standup and lose context across docs.</p></div>
            </div>
          </div>
          <div class="child"></div>
        </div>
        """
        body = extract_op_body_from_post_html(html)
        self.assertIn("blockers too late", body)
        self.assertIn("lose context", body)

    def test_score_candidate(self) -> None:
        score, flags = score_candidate(
            "I spend time figuring out what is going on",
            "We keep finding blockers too late and Slack context gets lost.",
        )
        self.assertGreaterEqual(score, 4)
        self.assertTrue(flags["first_person"])
        self.assertTrue(flags["pain_signal"])
        self.assertTrue(flags["coordination_signal"])


if __name__ == "__main__":
    unittest.main()
