CREATE TABLE Vendors (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [name] VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Models (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [vendor_id] INT NOT NULL,
    [model_name] VARCHAR(100) NOT NULL, 
    FOREIGN KEY ([vendor_id]) REFERENCES Vendors([id])
);

CREATE TABLE Games (
    [token] VARCHAR(100) PRIMARY KEY,
    [map] VARCHAR(100) NOT NULL,
	[max_distance_km] FLOAT NOT NULL,
    [rounds_count] INT NOT NULL,
    [total_score] INT,
    [total_distance_km] FLOAT,
	[start_datetime_utc] DATETIME,
    [player_id] VARCHAR(100)
);

CREATE TABLE Rounds (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [game_token] VARCHAR(100) NOT NULL,
    [round_number] INT NOT NULL,
    [panorama_id] VARCHAR(255),
    [image_url] VARCHAR(512),
    [true_latitude] FLOAT NOT NULL,
    [true_longitude] FLOAT NOT NULL,
    [true_country_code] VARCHAR(2) NOT NULL,
	[aggregated_latitude] FLOAT NOT NULL,
    [aggregated_longitude] FLOAT NOT NULL,
    [aggregated_country_code] VARCHAR(2),
    [score] INT NOT NULL,
    [distance_km] FLOAT NOT NULL,
    FOREIGN KEY ([game_token]) REFERENCES Games([token])
);

CREATE TABLE Guesses (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [round_id] INT NOT NULL,
    [model_id] INT NOT NULL,
    [latitude] FLOAT,
    [longitude] FLOAT,
	[country_code] VARCHAR(2),
    [reasoning] VARCHAR(MAX) NOT NULL,
	[seconds_spent] INT NOT NULL,
    [score] INT,
    [distance_km] FLOAT,
    FOREIGN KEY ([round_id]) REFERENCES Rounds([id]),
    FOREIGN KEY ([model_id]) REFERENCES Models([id])
);