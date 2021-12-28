sbcl --load quicklisp.lisp
(ql:quickload "cl-csv")
(defparameter data (cl-csv:read-csv #P"data.csv"))


(defparameter score_values ())
(loop for a in data
   do (push (nth 0 (with-input-from-string (in (nth 1 a))
  (loop for x = (read in nil nil) while x collect x))) score_values))

(defparameter time_values ())
(loop for a in data
   do (push (nth 0 (with-input-from-string (in (nth 2 a))
  (loop for x = (read in nil nil) while x collect x))) time_values))

(defparameter mean_time 0)
(setq mean_time (/ (apply '+ time_values) (length time_values)))

(defparameter mean_score 0)
(setq mean_score (/ (apply '+ score_values) (float (length score_values))))

(defparameter variance_score 0)
(setq variance_score (/ (apply '+ (mapcar (lambda (x) (* x x)) (mapcar (lambda (n) (- n mean_score))
        score_values))) (length score_values)))

(defparameter variance_time 0)
(setq variance_time (/ (apply '+ (mapcar (lambda (x) (* x x)) (mapcar (lambda (n) (- n mean_time))
        time_values))) (length time_values)))

mean_time
variance_time 
mean_score
variance_score

