# docs/source/conf.py

import os
import sys
from datetime import datetime
from sphinx.ext import autodoc

# -- Path setup --------------------------------------------------------------

# Додаємо корінь проєкту, щоб імпортувати app
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = 'PhotoShare'
author = 'Natala Bodnarcuk'
copyright = f'{datetime.now().year}, {author}'
release = '1.0.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',   # для Google/NumPy стилю docstring
    'sphinx.ext.viewcode',   # додати посилання на код
    'sphinx.ext.todo',       # якщо хочеш todo
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Mock імпорти, щоб не падало через Pydantic Settings або зовнішні пакети
autodoc_mock_imports = [
    "app.conf.config",
    "app.database.connect_db",
    "app.services.auth",
    "app.services.email",
    "app.services.roles",
    "app.services.templates",
    "app.database",
    "sqlalchemy",
    "cloudinary",
    "redis",
]

# Автогенерація summary
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Load fake environment for docs -----------------------------------------

from dotenv import load_dotenv

# Якщо хочеш — можна створити окремий .env.docs із фейковими змінними
load_dotenv(dotenv_path=os.path.abspath("../../.env.docs"))

# -- Napoleon settings -------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True

# -- Autodoc default options -------------------------------------------------

autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']
autodoc_typehints = 'description'
