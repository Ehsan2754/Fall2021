import CodeWorld
main :: IO ()

-- | A grid represented as a list of rows of "things".
data Grid a = Grid [[a]]

-- * A grid of pictures

-- | Picture of a wall.
wallPicture :: Picture
wallPicture = solidRectangle 0.95 0.95

-- | Picture of a floor.
floorPicture :: Picture
floorPicture = colored (light (light gray)) (solidRectangle 0.95 0.95)

-- | Doors will be differentiated by their index.
type DoorId = Int

-- | Doors and keys are distinguished visually using color.
doorIdColor :: DoorId -> Color
doorIdColor 0 = red
doorIdColor 1 = blue
doorIdColor 2 = green
doorIdColor n = light (doorIdColor (n - 3))

-- | Picture of a door with a given index.
doorPicture :: DoorId -> Picture
doorPicture doorId
  = colored (doorIdColor doorId) (solidCircle 0.3)
 <> wallPicture

-- | Picture of a key for a door with a given index.
keyPicture :: DoorId -> Picture
keyPicture doorId
  = scaled 0.5 0.5 (lettering "🔑")
 <> colored (doorIdColor doorId) (solidCircle 0.42)
 <> floorPicture 

-- | Picture of a coin.
coinPicture :: Picture
coinPicture = scaled 0.7 0.7 (lettering "🍎") <> floorPicture

-- | A sample grid of pictures.
myPictureGrid :: Grid Picture
myPictureGrid = Grid
  [ [ w, w, w, w, w, w, w, w, w ]
  , [ w, c, w, f, f, f, w, f, w ]
  , [ w, f, w, f, w, f, f, f, w ]
  , [ w, f, f, f, w, w, w, f, w ]
  , [ w, f, w, f, w, f, f, f, w ]
  , [ w, f, w, w, w, w, d, w, w ]
  , [ w, f, w, c, w, f, f, f, w ]
  , [ w, k, w, f, f, f, w, c, w ]
  , [ w, w, w, w, w, w, w, w, w ]
  ]
  where
    w = wallPicture
    f = floorPicture
    k = keyPicture 1
    d = doorPicture 1
    c = coinPicture
    
-- | Exercise 6.1.
-- Implement this function. Try using higher-order functions.
renderGrid :: Grid Picture -> Picture
renderGrid (Grid rows) = blank
fun :: [a]->[[a]]

main = drawingOf (scaled 2 2 (translated (-4) 4 (renderGrid myPictureGrid)))