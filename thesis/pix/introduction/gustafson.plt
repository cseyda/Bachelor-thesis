cd 'D:\Desktop\BA_Arbeit\thesis\pix\introduction'


set terminal pdfcairo enhanced mono size 3,3 dashed font "Linux Biolinum"

set xlabel "Number of Processors"
set ylabel "Speedup" 

set xrange [0:120]
set yrange [0:120] 

#set size ratio 2
set output "gustafson.pdf"
set key left top
set pointsize 2
set grid

f(x, N) = x-( 1-N )*( x-1 )

plot f(x, 0.500) title "50%" lt 2 lw 5,\
     f(x, 0.750) title "75%" lt 5 lw 5,\
     f(x, 0.900) title "90%" lt 3 lw 5,\
     f(x, 0.950) title "95%" lt 4 lw 5