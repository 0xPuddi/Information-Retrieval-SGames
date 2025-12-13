run:
	cd ./app
	npm i
	npx @tailwindcss/cli -i ./public/style.css -o ./public/output.css
	cd ..
	uv run app

scrapers:
	uv run scraper

tex:
	@mkdir -p ./report
	@touch ./report/references.bib
	pdflatex -output-directory=./report ./report/report.tex
	-cd ./report && bibtex report
	pdflatex -output-directory=./report ./report/report.tex
	pdflatex -output-directory=./report ./report/report.tex
	@mv ./report/report.pdf ./report.pdf
	@echo "PDF generated at ./report.pdf"
