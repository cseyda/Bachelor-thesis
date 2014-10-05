cd 'D:\Desktop\BA_Arbeit\thesis\pix\systemconsumption'

set output "systemconsumption.pdf"
set terminal pdfcairo mono size 6,2 font "Linux Biolinum"

set ylabel "P [W]" 
set grid

set style data histograms
set style histogram rowstacked
 
set style fill pattern border lt -1
set boxwidth 0.7

set key invert

#plot 'data.txt' using 2:xtic(1) ti col, '' u 3 ti col, '' u 4 ti col, '' u 5 ti col, '' u 6 ti col
plot for [COL=2:6] 'data.txt' using COL:xtic(1) ti col