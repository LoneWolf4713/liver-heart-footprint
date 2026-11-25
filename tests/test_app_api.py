"""Unit and integration tests for Deliverable 4 backend (app.scraper & app.main)."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.scraper import RecipeScrapeError, extract_recipe_from_html, parse_servings, validate_public_http_url


SAMPLE_JSONLD_HTML = """<!doctype html>
<html>
<head>
  <title>Paneer Butter Masala Recipe - Demo Site</title>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {"@type": "WebSite", "name": "Demo"},
      {
        "@type": ["Recipe"],
        "name": "Paneer Butter Masala",
        "recipeYield": "4 servings",
        "recipeIngredient": [
          "200 g paneer, cubed",
          "2 tbsp butter",
          "1 tbsp oil",
          "2 large tomatoes",
          "salt to taste"
        ]
      }
    ]
  }
  </script>
</head>
<body></body>
</html>"""


class TestAppBackendAndScraper(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_parse_servings_variants(self):
        self.assertEqual(parse_servings(4)[0], 4.0)
        self.assertEqual(parse_servings("Makes 12 samosas")[0], 12.0)
        self.assertEqual(parse_servings(["6 servings", "6"])[0], 6.0)
        self.assertIsNone(parse_servings("to serve")[0])

    def test_validate_public_http_url_rejects_local(self):
        for bad in ("", "ftp://example.com/a", "http://localhost:8000/test", "http://127.0.0.1/test"):
            with self.assertRaises(RecipeScrapeError):
                validate_public_http_url(bad)

    def test_extract_recipe_from_jsonld_graph(self):
        out = extract_recipe_from_html(SAMPLE_JSONLD_HTML, url="https://example.com/pbm")
        self.assertEqual(out["dish"], "Paneer Butter Masala")
        self.assertEqual(out["servings"], 4.0)
        self.assertEqual(len(out["lines"]), 5)
        self.assertEqual(out["scrape_meta"]["source"], "json-ld")

    def test_health_and_lab_data_endpoints(self):
        r_health = self.client.get("/api/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["status"], "ok")
        self.assertEqual(r_health.json()["lab_rows"], 69)

        r_lab = self.client.get("/api/lab-data")
        self.assertEqual(r_lab.status_code, 200)
        self.assertEqual(r_lab.json()["count"], 69)

        r_home = self.client.get("/")
        self.assertEqual(r_home.status_code, 200)
        self.assertIn("Liver &amp; Heart Footprint", r_home.text)

    def test_analyze_paste_samosa_with_setting_and_provenance(self):
        payload = {
            "dish": "samosa",
            "servings": 8,
            "lines": "2 cups maida\n3 medium potatoes\n500 ml oil for deep frying\nsalt to taste",
            "setting": "urban",
            "risk": "general",
            "frying_setting": "street",
        }
        resp = self.client.post("/api/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        fc = data["frying_correction"]
        self.assertTrue(fc["applied"])
        self.assertEqual(fc["setting_requested"], "street")
        self.assertEqual(fc["setting_used"], "street")
        self.assertFalse(fc["fallback_used"])
        self.assertIn("absorbed_fat_g =", fc["calculation_formula"])
        self.assertGreater(len(fc["matched_sources"]), 0)
        self.assertGreater(fc["non_oil_mass_g"], 0)

    def test_analyze_missing_servings_safely_falls_back(self):
        payload = {
            "dish": "dal",
            "servings": None,
            "lines": ["1 cup toor dal", "1 tbsp ghee", "salt to taste"],
        }
        resp = self.client.post("/api/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["per_serving"])
        self.assertIsNotNone(data["footprint"])
        self.assertTrue(data["recipe"]["servings_missing"])
        self.assertTrue(any(w.startswith("NO_SERVINGS") for w in data["warnings"]))

    def test_scrape_and_analyze_endpoint(self):
        with patch("app.main.scrape_recipe_url") as mock_scrape:
            mock_scrape.return_value = extract_recipe_from_html(
                SAMPLE_JSONLD_HTML, url="https://hebbarskitchen.com/paneer-butter-masala-recipe/"
            )
            resp = self.client.post(
                "/api/scrape-and-analyze",
                json={"url": "https://hebbarskitchen.com/paneer-butter-masala-recipe/", "risk": "cardiometabolic"},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["recipe"]["dish"], "Paneer Butter Masala")
        self.assertAlmostEqual(data["footprint"]["axes"]["sfa_g"]["limit"], 17.4222, places=2)
        self.assertEqual(data["scrape_meta"]["source"], "json-ld")


if __name__ == "__main__":
    unittest.main()
