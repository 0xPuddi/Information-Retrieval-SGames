run:
	cd ./app && npm i && npx @tailwindcss/cli -i ./public/style.css -o ./public/output.css
	uv run app

scrapers:
	uv run scraper

tex:
	cd ./report && pdflatex report.tex
	cd ./report && biber report
	cd ./report && pdflatex report.tex
	cd ./report && pdflatex report.tex
	@mv ./report/report.pdf ./report.pdf
	@echo "PDF generated at ./report.pdf"
