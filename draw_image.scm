(let* ((image (car (gimp-image-new 800 600 RGB)))
       (layer (car (gimp-layer-new image 800 600 RGB-IMAGE "Background" 100 NORMAL-MODE)))
       (drawable 0))
  
  (gimp-image-insert-layer image layer 0 0)
  (gimp-context-set-foreground '(255 255 255))
  (gimp-drawable-fill layer FILL-FOREGROUND)
  
  ; Nakreslí slunce
  (gimp-context-set-foreground '(255 255 0))
  (gimp-image-select-ellipse image CHANNEL-OP-REPLACE 600 50 150 150)
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image)
  
  ; Nakreslí oblohu (modrý gradient)
  (gimp-context-set-foreground '(135 206 235))
  (gimp-image-select-rectangle image CHANNEL-OP-REPLACE 0 0 800 300)
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image)
  
  ; Nakreslí trávu (zelená)
  (gimp-context-set-foreground '(34 139 34))
  (gimp-image-select-rectangle image CHANNEL-OP-REPLACE 0 300 800 300)
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image)
  
  ; Nakreslí domeček
  (gimp-context-set-foreground '(139 69 19))
  (gimp-image-select-rectangle image CHANNEL-OP-REPLACE 250 350 300 200)
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image)
  
  ; Nakreslí střechu (červená)
  (gimp-context-set-foreground '(178 34 34))
  (gimp-image-select-polygon image CHANNEL-OP-REPLACE 6 (vector 250 350 400 250 550 350))
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image)
  
  ; Uloží obrázek
  (file-png-save RUN-NONINTERACTIVE image layer "/home/jirka/cml/obrazek.png" "/home/jirka/cml/obrazek.png" 0 9 0 0 0 0 0)
  
  (gimp-image-delete image))

(gimp-quit 0)
