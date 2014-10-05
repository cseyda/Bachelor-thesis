cd 'D:\Desktop\BA_Arbeit\thesis\pix\pstates'

set output "pstates.pdf"
set terminal pdfcairo mono dashed font "Linux Biolinum"

set xlabel "f [GHz]"
set ylabel "U [V]" 
set xrange [0:3]
set yrange [0.8:1.4] 

set key right bottom
set pointsize 2
set grid

f(x)=a*x+b
fit f(x) "core2x6800.txt" via a, b

g(x)=c*x+d
fit g(x) "a64x24800.txt" via c, d

h(x)=e*x+f
fit h(x) "a64x23600.txt" via e, f

plot "core2x6800.txt" title "Core 2 Extreme X6800" with linespoints pt 9 lw 5,\
     f(x) title "linear regression X6800" lt 2 lw 3,\
     "a64x24800.txt" title "Athlon A64 X2 4800+" with linespoints pt 8 lw 5,\
     g(x) title "linear regression 4800+" lt 3 lw 3,\
     "a64x23600.txt" title "Athlon A64 X2 3600+" with linespoints pt 10 lw 5,\
     h(x) title "linear regression 3600+" lt 4 lw 3