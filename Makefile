cli:
	python  -m  src.main_cli


web:
	fastapi dev src/main_web.py

test:
	@echo "Running tests..."
	@pytest -v --tb=short --disable-warnings tests/
	@echo "Tests completed."


check:
	@echo "Checking Python syntax..."
	@python -m py_compile src/**/*.py src/*.py
	@echo "Checking imports..."
	@python -c "import src.main_cli; import src.main_web; print('All imports successful')"
	@echo "All checks passed!"