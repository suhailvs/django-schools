=======================
Chapter 1: Introduction
=======================

Overview
========
This project is a Django-based Quiz application supporting multiple user types (students and teachers). Teachers create quizzes with multiple-choice questions, and students attempt them. The codebase enforces role-based access, test-driven development, and user experience consistency.

Project Structure
-----------------

- **classroom/**: Main Django app containing models, views, forms, tests, and URLs for quiz functionality.
- **mysite/**: Django project settings and root URLs.
- **templates/**: HTML templates for rendering views.
- **static/**: Static files (CSS, JS, images).
- **docs/**: Sphinx documentation.

Key Components
--------------

- **Models**: `User`, `Student`, `Quiz`, `Question`, `Answer`, `TakenQuiz`, `StudentAnswer`, etc.
- **Views**: Split by user type (`classroom/views/teachers.py`, `classroom/views/students.py`).
- **Forms**: Used for quiz creation, question management, and quiz attempts.
- **Tests**: Unittests in `classroom/tests.py` ensure permissions, quiz logic, and user experience.
- **Fixtures**: Sample data in `classroom/fixtures/datas.json` for testing and development.

Development Workflow
--------------------

1. **Setup**: Install dependencies from `requirements.txt` and apply migrations.
2. **Testing**: Run `python manage.py test classroom` to execute unittests. Coverage and linting are enforced.
3. **User Roles**: Teachers can create/edit/delete quizzes; students can attempt quizzes and view results.
4. **Templates**: Use Bootstrap for consistent UI. Navigation and feedback are tested for both roles.
5. **Documentation**: Sphinx docs are in the `docs/` folder. Build with `make html`.

How to Build Documentation
--------------------------

1. Install Sphinx: `pip install sphinx`
2. Navigate to the `docs/` folder.
3. Run `make html` to build HTML documentation.
4. Open `_build/html/index.html` in your browser to view docs.

Extending the Project
---------------------
- Add new models in `classroom/models.py` and run migrations.
- Add new views/forms/templates for features.
- Write unittests for all new code in `classroom/tests.py`.
- Update documentation in `docs/` as features are added.

For more details, see the source code and existing Sphinx docs in the `docs/` folder.
