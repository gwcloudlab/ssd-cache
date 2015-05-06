

paper:
	# sh figures/getfigs.sh
	pdflatex paper
	bibtex paper
	pdflatex paper
	pdflatex paper

zip:
	tar czf paper.tgz *.tex figures/ *.bib *.cls Makefile

texzip:
	tar czf paper.tgz *.tex *.bib *.cls Makefile

clean:
	rm paper.aux paper.bbl paper.blg paper.log

