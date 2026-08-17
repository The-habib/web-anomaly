"""Negative control tests to ensure Atlas NEVER labels ordinary websites as anomalies."""

import unittest
from atlas.core.models import TimelineEvent, EvidenceState
from atlas.scoring.scorer import AnomalyScorer

class TestNegativeControls(unittest.TestCase):

    def setUp(self):
        self.scorer = AnomalyScorer()

    def test_modern_static_website(self):
        """A modern static website with standard modern DOM should score 0."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Static Product Page</title>
</head>
<body class="bg-gray-100 text-gray-900 font-sans">
    <header class="p-6 bg-white shadow-md">
        <h1 class="text-2xl font-bold">Acme Analytics Platform</h1>
    </header>
    <main class="max-w-4xl mx-auto py-12 px-4">
        <p class="text-lg">Modern cloud-native telemetry for high-scale microservices.</p>
    </main>
</body>
</html>"""
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={"doctype": "<!DOCTYPE html>", "generator": ""},
            html_content=html,
            live_status=200
        )
        self.assertEqual(score, 0)
        self.assertEqual(classification, "Standard Web Surface")
        self.assertIn(state, (EvidenceState.OBSERVED, EvidenceState.INSUFFICIENT))
        self.assertGreaterEqual(conf, 0.90)

    def test_article_discussing_legacy_html(self):
        """A modern blog post containing legacy tags inside code blocks should NOT trigger fossil signals."""
        html = """<!DOCTYPE html>
<html>
<head><title>Web Development History: The 1990s Tag Wars</title></head>
<body>
    <article class="blog-post">
        <h1>Remembering the Marquee and Font Tags</h1>
        <p>In early versions of the web, developers used archaic tags like:</p>
        <pre><code>&lt;marquee&gt;Scrolling Text&lt;/marquee&gt;</code></pre>
        <p>They also styled inline text with <code>&lt;font color="red"&gt;</code> before CSS took over.</p>
        <blockquote>
            <p>Deprecated tags should never be used in modern HTML5 production.</p>
        </blockquote>
    </article>
</body>
</html>"""
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        # Fossil signal must NOT fire on code/article content
        fossil_signals = [s for s in signals if s.signal_id == "technology_fossil" and s.score_awarded > 0]
        self.assertEqual(len(fossil_signals), 0)
        self.assertEqual(score, 0)

    def test_standard_corporate_robots(self):
        """Standard robots.txt with routine disallows should NOT trigger anomalies."""
        html = "<html><body><h1>Corporate Homepage</h1></body></html>"
        metadata = {
            "robots_txt": {"has_unusual_disallows": False, "disallows": ["/admin/", "/login/"]}
        }
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata=metadata,
            html_content=html,
            live_status=200
        )
        self.assertEqual(score, 0)
        self.assertEqual(classification, "Standard Web Surface")

    def test_standard_empty_directory_index(self):
        """Standard web server directory listing without historical artifacts should score 0."""
        html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /uploads</title>
 </head>
 <body>
<h1>Index of /uploads</h1>
<ul><li><a href="/"> Parent Directory</a></li>
<li><a href="test.txt"> test.txt</a> 2026-08-10 12:00 120</li>
<li><a href="logo.png"> logo.png</a> 2026-08-15 08:30 4.2K</li>
</ul>
</body></html>"""
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        # Should not award points for forgotten archive
        arch_signals = [s for s in signals if s.signal_id == "forgotten_archive" and s.score_awarded > 0]
        self.assertEqual(len(arch_signals), 0)

if __name__ == "__main__":
    unittest.main()
