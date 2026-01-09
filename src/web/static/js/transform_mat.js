//cote plein quand pas (mur ou vide)

export function transform_mat(m){
    //m est une matrice contenant le contenu des cases 
    //la sortie est une matrice contenant quelle texture afficher
    //un mur sera ecrit avec les points cardinaux montrant ses côtés pleins
    //par exemple un mur plein en haut sera "wallT"
    //un mur plein en haut et a droite sera "wallTE"
    //l'ordre des points cardinaux est BITE (bas, izquierda, top, east)

    let new_m = Array(m.length).fill(null).map(() => Array(m[0].length).fill(0));

    for(let i = 0; i <m.length; i++){
        for(let j = 0; j < m[i].length; j++){

            new_m[i][j] = m[i][j]

            if (m[i][j] == "wall"){

                if(i+1 < m.length){
                    if (m[i+1][j] != "wall" && m[i+1][j] != "void"){
                        new_m[i][j] = new_m[i][j].concat("B");
                    }
                }

                if (j-1 > 0){
                    if (m[i][j-1] != "wall" && m[i][j-1] != "void"){
                        new_m[i][j] = new_m[i][j].concat("I");
                    }
                }
                
                if(i-1 > 0){
                    if (m[i-1][j] != "wall" && m[i-1][j] != "void"){
                        new_m[i][j] = new_m[i][j].concat("T");
                    }
                }
                
                if (j+1 < m[i].length){
                    if (m[i][j+1] != "wall" && m[i][j+1] != "void"){
                        new_m[i][j] = new_m[i][j].concat("E");
                    }
                }
            }
        }

    }
    
    return new_m
}
