"""Template regression checks; no media files, credentials, or network required.

Run with: python -m unittest discover -s tests -v
"""

import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


TEMPLATES = Path(__file__).resolve().parents[1] / "templates"


class Markup(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.forms = []
        self.current_form = None
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        self.elements.append((tag, attributes))
        if tag == "form":
            self.current_form = {**attributes, "fields": set()}
            self.forms.append(self.current_form)
        elif self.current_form is not None and tag in {"input", "select", "textarea"}:
            if attributes.get("name"):
                self.current_form["fields"].add(attributes["name"])

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None


class TemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = Environment(
            loader=FileSystemLoader(TEMPLATES),
            autoescape=select_autoescape(("html",)),
            undefined=StrictUndefined,
        )

    def render(self, template, **context):
        source = self.environment.get_template(template).render(**context)
        markup = Markup(source)
        ids = [attrs["id"] for _, attrs in markup.elements if attrs.get("id")]
        self.assertEqual([], [key for key, count in Counter(ids).items() if count > 1])
        for tag, attrs in markup.elements:
            for attribute in ("aria-labelledby", "aria-describedby", "aria-controls"):
                for target in attrs.get(attribute, "").split():
                    self.assertIn(target, ids, f"Missing {attribute} target: {target}")
            if tag == "label" and attrs.get("for"):
                self.assertIn(attrs["for"], ids)
            asset = attrs.get("src") if tag == "script" else attrs.get("href") if tag == "link" else ""
            if asset and asset.startswith("/templates/"):
                self.assertTrue((TEMPLATES / asset.removeprefix("/templates/").split("?")[0]).is_file(), asset)
        return source, markup

    def assert_post_fields(self, markup, action, expected):
        forms = [form for form in markup.forms if form.get("action") == action]
        self.assertTrue(forms, f"Missing form: {action}")
        for form in forms:
            self.assertEqual("post", form.get("method", "").lower())
            self.assertTrue(set(expected).issubset(form["fields"]), form)

    @staticmethod
    def home_context():
        return dict(videos=[], images=[], musics=[], download_success="", download_error="")

    @staticmethod
    def cloud_context(configured=False, linked=False):
        providers = [dict(name=name, display=display, configured=configured, linked=linked)
                     for name, display in (("google", "Google Drive"), ("onedrive", "OneDrive"), ("dropbox", "Dropbox"))]
        return dict(providers=providers, active=providers[0], folder="", files=[], cloud_images=[], error="")

    def test_empty_home_keeps_import_forms(self):
        _, markup = self.render("index.html", **self.home_context())
        self.assert_post_fields(markup, "/upload", {"files"})
        self.assert_post_fields(markup, "/download-youtube", {"url", "media_type"})
        self.assertFalse(any(form.get("action") == "/delete" for form in markup.forms))

    def test_home_media_keeps_backend_contract_and_escapes_names(self):
        context = self.home_context()
        filename = 'Holiday <script>alert("x")</script> & family.mp4'
        context.update(
            videos=[dict(name=filename, size=12.5, date="2026-09-08", thumbnail=None, thumbnail_name="", bgm="")],
            images=[dict(name="Cover & artwork.jpg", size=0.2, url="/media/cover.jpg")],
            musics=[dict(name="Music.mp3", size=3.2, url="/media/music.mp3")],
        )
        source, markup = self.render("index.html", **context)
        self.assertNotIn('<script>alert("x")</script>', source)
        self.assertIn("&lt;script&gt;", source)
        self.assert_post_fields(markup, "/assign-thumbnail", {"video_name", "thumbnail_name"})
        self.assert_post_fields(markup, "/assign-bgm", {"video_name", "bgm_name"})
        self.assert_post_fields(markup, "/delete", {"filename"})
        delete_forms = [form for form in markup.forms if form.get("action") == "/delete"]
        self.assertEqual(3, len(delete_forms))

    def test_delete_preserves_scroll_position_across_redirect(self):
        script = (TEMPLATES / "app.js").read_text(encoding="utf-8")
        self.assertIn('sessionStorage.setItem(deleteScrollKey, String(window.scrollY))', script)
        self.assertIn('sessionStorage.removeItem(deleteScrollKey)', script)
        self.assertIn('window.scrollTo(0, scrollY)', script)

    def test_cloud_setup_and_connection_states(self):
        for configured, linked in ((False, False), (True, False), (True, True)):
            with self.subTest(configured=configured, linked=linked):
                _, markup = self.render("cloud.html", **self.cloud_context(configured, linked))
                auth_links = [attrs for tag, attrs in markup.elements if tag == "a" and attrs.get("href") == "/cloud/google/auth"]
                self.assertEqual(configured and not linked, bool(auth_links))
                if linked:
                    self.assert_post_fields(markup, "/cloud/google/upload", {"files", "folder"})
                    self.assert_post_fields(markup, "/cloud/google/logout", set())

    def test_cloud_mixed_media_preserves_actions(self):
        context = self.cloud_context(True, True)
        files = [dict(kind=kind, name=f"Example {kind}", file_id=f"id-{kind}", size_mb=1,
                      folder_url="/cloud?provider=google&folder=example", stream_url="/sample",
                      thumb_url="", can_save_to_media=kind != "folder")
                 for kind in ("folder", "video", "image", "audio")]
        files[1].update(thumbnail_id="", assigned_thumbnail_url="")
        context.update(files=files, cloud_images=[files[2]], folder="example-folder")
        _, markup = self.render("cloud.html", **context)
        self.assert_post_fields(markup, "/cloud/google/assign-thumbnail", {"video_id", "thumbnail_id", "folder"})
        self.assert_post_fields(markup, "/cloud/google/save-to-media", {"file_id", "filename", "folder"})
        save_forms = [form for form in markup.forms if form.get("action") == "/cloud/google/save-to-media"]
        self.assertEqual(3, len(save_forms))


if __name__ == "__main__":
    unittest.main()
