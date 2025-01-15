#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Copyright 2025 Martin Bukatovič <martinb@marbu.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import datetime
import os.path
import sys
import textwrap


class PageType:
    """
    Definition of a wiki page type, including it's format (syntax), gitit
    header and content templates.
    """

    def __init__(self, name, page_format, description, template=None):
        self.name = name
        self.page_format = page_format
        self.description = description
        self.template = template

    def get_header(self, project_name, title, extra_categories, subpage):
        """
        Generate string with gitit header of a wiki page.
        """
        categories = ["wiki-new", self.name, f"project-{project_name}"]
        if extra_categories is not None:
            categories.extend(extra_categories)
        categories_str = ' '.join(categories)
        title_str = title.capitalize()
        if subpage is not None:
            title_str += " " + subpage.capitalize()
        if self.name != "main":
            title_str += " " + self.name.capitalize()
        header = textwrap.dedent(f"""\
            ---
            format: {self.page_format}
            categories: {categories_str}
            title: {title_str}
            ...
            """)
        return header

    def get_content(self):
        if self.template is None:
            return ""
        return self.template

    def create_file(self, project_name, title, categories, wiki_dir, subpage, dry_run=False):
        """
        Create wiki page file with initial content based on templates.
        """
        if self.name == "main":
            file_name = f"{project_name}.page"
        elif subpage is not None:
            file_name = f"{project_name}.{subpage}.{self.name}.page"
        else:
            file_name = f"{project_name}.{self.name}.page"
        if title is None:
            title = project_name
        file_head = self.get_header(project_name, title, categories, subpage)
        file_data = self.get_content()
        file_path = os.path.join(wiki_dir, file_name)
        if dry_run:
            print(file_path)
            print(file_head)
            print(file_data)
            return
        if os.path.exists(file_path):
            print(f"wiki page '{file_name}' already exists, skipping")
            return
        with open(file_path, "w") as fo:
            fo.write(file_head)
            fo.write(file_data)


class LablogPageType(PageType):

    def get_content(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        lines = [
            f"* {today}",
            "** Establishing lablog",
            "- created this lablog via ~wiki-new~ tool"
            ]
        return "\n".join(lines)


PAGE_TYPES = {
    "main": PageType(
        "main",
        "markdown",
        "default wiki/overview page, always created"),
    "lablog": LablogPageType("lablog", "org", "lablog aka work journal"),
    "orienting": PageType(
        "orienting",
        "markdown",
        "thinking and planning",
        template=textwrap.dedent("""
            ## What I'm trying to solve?

            ## What to review/learn?

            ## What do I need to do?
            """)),
    "checklist": PageType(
        "checklist",
        "markdown",
        "SOP (standard operating procedure) like checklist",
        template=textwrap.dedent("""
            ## Procedure

            - [ ] step one
            - [ ] step two
            """)),
    "progress": PageType("progress", "org", "ad-hoc status/todo list")
    }


def get_page_type_help():
    """
    Generate help string for argparse raw help formatter explaining various
    wiki page types.
    """
    help_lines = ["wiki page types (valid PAGETYPE values):"]
    for name, page in PAGE_TYPES.items():
        help_lines.append(f"  {name:18s} {page.description}")
    return "\n".join(help_lines)


def main():
    ap = argparse.ArgumentParser(
        description="initialize set of wiki pages for a given project/topic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=get_page_type_help())
    ap.add_argument("project", help="name prefix for all created wiki pages")
    ap.add_argument(
        "-p",
        dest="pages",
        nargs="*",
        choices=PAGE_TYPES.keys(),
        metavar="PAGETYPE",
        default=["main"],
        help="wiki page types to create (default used when not specified)")
    ap.add_argument(
        "-t",
        dest="title",
        help="title prefix for created wiki pages")
    ap.add_argument(
        "-c",
        dest="categories",
        nargs="*",
        metavar="CAT",
        help="categories to be added to created wiki pages")
    ap.add_argument(
        "-d",
        dest="dir",
        default="",
        help="directory to create pages in (wiki root used if not specified)")
    ap.add_argument(
        "-s",
        dest="subpage",
        help="subpage name, use when you need multiple pages of the same type")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="don't actually create the pages, show them on stdout")
    args = ap.parse_args()

    for page_t in args.pages:
        page = PAGE_TYPES.get(page_t)
        page.create_file(
            project_name=args.project,
            title=args.title,
            categories=args.categories,
            wiki_dir=args.dir,
            subpage=args.subpage,
            dry_run=args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
