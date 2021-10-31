#lang slideshow
(require 2htdp/image)
(define (ex-sin x)(abs (+ 100 (* 50 (sin x)))))
(define (plot-bars x) (
                       cond [(empty? x) (blank)] 
                          [(
hb-append 5(rectangle 10 (car x) "solid" "red")
          (plot-bars (cdr x)))
                           ]
                     
                       )
  )
(plot-bars (map ex-sin (range 0 10 0.2)))