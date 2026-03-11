CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE subcategorias (
    id_subcategoria SERIAL PRIMARY KEY,
    id_categoria INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT fk_subcategorias_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    UNIQUE (id_categoria, nombre)
);

CREATE TABLE productos (
    id_producto SERIAL PRIMARY KEY,
    id_subcategoria INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    precio_kg_ars DECIMAL(10,2) NOT NULL CHECK (precio_kg_ars >= 0),
    es_estacional BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_productos_subcategoria
        FOREIGN KEY (id_subcategoria)
        REFERENCES subcategorias(id_subcategoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    UNIQUE (id_subcategoria, nombre)
);

CREATE TABLE recetas (
    id_receta SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    instrucciones TEXT
);

CREATE TABLE receta_ingredientes (
    id_receta_ingrediente SERIAL PRIMARY KEY,
    id_receta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_gramos INT NOT NULL CHECK (cantidad_gramos > 0),
    CONSTRAINT fk_ri_receta
        FOREIGN KEY (id_receta)
        REFERENCES recetas(id_receta)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_ri_producto
        FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    UNIQUE (id_receta, id_producto)
);
