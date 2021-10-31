;; Conway's game of life
;; source : 
;; https://github.com/kflu/game-of-life-racket

#lang racket
#lang racket
(require (planet neil/charterm:3:0))
(provide (all-defined-out))
(define (make-matrix m n) (for/vector ([i (in-range 0 m)]) (make-vector n 0)))
(define (mat-ref mat x y) (vector-ref (vector-ref mat x) y))
(define (mat-set! mat x y v) (vector-set! (vector-ref mat x) y v))

(define (mat-dimension mat) 
  (cons (vector-length mat)
        (vector-length (vector-ref mat 0))))

(define (in-range? low high v)
  (and 
    (low . <= . v)
    (v . < . high)))

(define (get-now board x y)
  (match-define (cons m n) (mat-dimension board))
  (let ([x (modulo (+ x m) m)]
        [y (modulo (+ y n) n)])
    (bitwise-and (mat-ref board x y) 1)))

(define (set-next! board x y v)
  (match-define (cons m n) (mat-dimension board))
  (let ([x (modulo (+ x m) m)]
        [y (modulo (+ y n) n)])
    (let* ([v (arithmetic-shift v 1)]
           [cur (mat-ref board x y)]
           [res (bitwise-ior cur v)])
      (mat-set! board x y res))))

(define (count-surround board x y)
  (+
    (get-now board (- x 1) (- y 1))
    (get-now board (- x 1) y)
    (get-now board (- x 1) (+ y 1))
    (get-now board x       (+ y 1))
    (get-now board (+ x 1) (+ y 1))
    (get-now board (+ x 1) y)
    (get-now board (+ x 1) (- y 1))
    (get-now board x       (- y 1))))

(define (update-board board)
  (match-define (cons m n) (mat-dimension board))
  (for* ([i (in-range 0 m)]
         [j (in-range 0 n)])
        (define surround (count-surround board i j))
        (cond
          [(= 1 (get-now board i j)) 
           (if (or (surround . < . 2)
                   (surround . > . 3))
             (set-next! board i j 0)
             (set-next! board i j 1))]
          [else (if (= surround 3) 
                     (set-next! board i j 1) 
                     (set-next! board i j 0))]))

  ; stage 2: move next state to current
  (for* ([i (in-range 0 m)]
         [j (in-range 0 n)])
        (define v (mat-ref board i j))
        (mat-set! board i j (arithmetic-shift v -1))))

(module* main #f

    (define SLEEP 0.2)

    ;; Clears the screen and put the cursor at (0,0) by using ANSI control sequence.
    ;; https://msdn.microsoft.com/en-us/library/windows/desktop/mt638032(v=vs.85).aspx
    (define (clear-screen) 
      (with-charterm
 (void (charterm-clear-screen))))

    (define (draw-board board)
      (match-define (cons m n) (mat-dimension board))
      (clear-screen)
      (for ([line board])
           (for ([c line]) (display (if (= (bitwise-and c 1) 0) "." "o")))
           (displayln "")))

    (define (make-mutable board)
      (match-define (cons m n) (mat-dimension board))
      (for/vector ([row board]) (for/vector ([v row]) v)))

    (define board
      (make-mutable
        #( 
           #(0 0 0 0 0 0 0 0 0 0)
           #(0 0 0 1 0 0 0 0 0 0)
           #(0 1 0 1 0 0 0 0 0 0)
           #(0 0 1 1 0 0 0 0 0 0)
           #(0 0 0 0 0 0 0 0 0 0)
           #(0 0 0 0 0 0 0 0 0 0)
           #(0 0 0 0 0 0 0 0 0 0)
           #(0 0 0 0 0 0 0 0 0 0)
           #(0 0 0 0 0 0 0 0 0 0)
           #(0 0 0 0 0 0 0 0 0 0)
           )))

    (draw-board board)
    (sleep SLEEP)

    (letrec ([loop (lambda () 
                     (update-board board)
                     (draw-board board)
                     (sleep SLEEP)
                     (loop))])
      (loop))

)