cd 'D:\Desktop\BA_Arbeit\thesis\pix\modelcompare'

set output "modelcompare.pdf"
set terminal pdfcairo size 5,3 enhanced mono dashed font "Linux Biolinum"

set xlabel "f [GHz]"
set ylabel "U [V]" 
set xrange [0:3]
set yrange [0:1.5] 

set key right bottom
set pointsize 2
set grid

gamma=0.94
beta=0.17
u=1.29
f=2.93

f(x)=u*x/f

g(x)=u*x/f+gamma*(1-x/f)

h(x)=u+beta*(x-f)

plot "c2ex6800.txt" title "Core 2 Extreme X6800" with linespoints pt 9 lw 3,\
    f(x) title "Frequency³" lt 2 lw 5,\
    g(x) title "Intercept approach" lt 3 lw 5,\
    h(x) title "Gradient approach" lt 4 lw 5