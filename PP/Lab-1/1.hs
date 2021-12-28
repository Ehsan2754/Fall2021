--t1
k ::(a->String) -> [a]->[IO()]
k g = map (\x -> putStrLn g x)

--t2
data Result a = Success a | Failure String deriving Show
divide :: Int -> Int -> Result Int 
divide _ 0 = Failure "division by zero"
divide n m = Success (n `div` m)
splitResults :: [Result a] -> ([String], [a])
splitResults x = (fl,sl)
    where 
        sl = map(\(Success x)->x)(filter isS x)
        fl = map(\(Success x)->x)(filter isF x)
        isS :: Result a -> Bool
        isS (Success a) = True
        isS _ = False
        isF :: Result a -> Bool
        isF (Failure a) = True
        isF _ = False  

example2 :: ([String],[Int])
example2 = splitResults (zipWith divide [6,7,8] [3 0 2] )

        
         
main :: IO()
main = print"t"