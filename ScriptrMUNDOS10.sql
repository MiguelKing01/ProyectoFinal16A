CREATE DATABASE mundo_virtual;

USE mundo_virtual;

-- Tabla de jugadores

CREATE TABLE jugadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(255) NOT NULL,
    nivel INT NOT NULL,
    puntuacion INT NOT NULL,
    equipo VARCHAR(255),
    inventario TEXT -- Agregamos una columna para almacenar los ítems e índices
);
drop table 	jugadores;
use mundo_virtual;

CREATE TABLE inventario (
    id_item INT PRIMARY KEY,  -- Eliminado el AUTO_INCREMENT
    id_jugador INT NOT NULL, 
    nombre_item VARCHAR(255) NOT NULL,
    descripcion_item TEXT NOT NULL,
    FOREIGN KEY (id_jugador) REFERENCES jugadores(id)
);

-- Tabla de partidas
CREATE TABLE partidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    equipo1 VARCHAR(255),
    equipo2 VARCHAR(255),
    resultado VARCHAR(255)
);

-- Tabla de mundos (grafo serializado como JSON)
CREATE TABLE mundos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grafo_serializado JSON
);

-- Tabla de ranking global

CREATE TABLE ranking (
    id_jugador INT,
    puntuacion INT,
    posicion INT,
    FOREIGN KEY (id_jugador) REFERENCES jugadores(id)
);
-- Procedimiento almacenado para registrar resultados y actualizar el ranking
DELIMITER $$

CREATE PROCEDURE registrar_partida(IN equipo1 VARCHAR(255), IN equipo2 VARCHAR(255), IN resultado VARCHAR(255), IN fecha DATE)
BEGIN
    DECLARE equipo1_puntos INT;
    DECLARE equipo2_puntos INT;
    
    -- Suponemos que si un equipo gana, gana 3 puntos, si empatan, ambos ganan 1 punto
    IF resultado = 'empate' THEN
        SET equipo1_puntos = 1;
        SET equipo2_puntos = 1;
    ELSEIF resultado = equipo1 THEN
        SET equipo1_puntos = 3;
        SET equipo2_puntos = 0;
    ELSE
        SET equipo1_puntos = 0;
        SET equipo2_puntos = 3;
    END IF;

    -- Insertamos la partida
    INSERT INTO partidas (fecha, equipo1, equipo2, resultado) 
    VALUES (fecha, equipo1, equipo2, resultado);

    -- Actualizamos el ranking
    CALL actualizar_ranking(equipo1, equipo1_puntos);
    CALL actualizar_ranking(equipo2, equipo2_puntos);
END $$

CREATE PROCEDURE actualizar_ranking(IN equipo VARCHAR(255), IN puntos INT)
BEGIN
    -- Suponemos que actualizamos la puntuación global de un jugador aquí
    DECLARE jugador_id INT;
    DECLARE nueva_puntuacion INT;
    
    -- Encontramos el jugador correspondiente al equipo
    SELECT id INTO jugador_id FROM jugadores WHERE equipo = equipo LIMIT 1;
    
    -- Actualizamos la puntuación
    UPDATE jugadores 
    SET puntuacion = puntuacion + puntos
    WHERE id = jugador_id;

    -- Recalcular ranking global
    SET @posicion = (SELECT COUNT(*) FROM jugadores WHERE puntuacion > nueva_puntuacion) + 1;
    INSERT INTO ranking (id_jugador, puntuacion, posicion)
    VALUES (jugador_id, nueva_puntuacion, @posicion)
    ON DUPLICATE KEY UPDATE puntuacion = nueva_puntuacion, posicion = @posicion;
END $$

DELIMITER ;