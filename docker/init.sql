-- Enable spatial extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Panneaux Associatifs (Marketing Panels)
DROP TABLE IF EXISTS panels;
CREATE TABLE panels (
    id UUID PRIMARY KEY,
    type TEXT,
    installation_date DATE,
    geom GEOMETRY(Point, 4326)  -- Longitude/Latitude
);

-- Bike Counters + Usage
DROP TABLE IF EXISTS bike_counts;
CREATE TABLE bike_counts (
    id UUID PRIMARY KEY,
    counter_name TEXT,
    date_time TIMESTAMP,
    count INTEGER,
    geom GEOMETRY(Point, 4326)
);

-- Commerces – Eau de Paris
DROP TABLE IF EXISTS commerces;
CREATE TABLE commerces (
    id UUID PRIMARY KEY,
    name TEXT,
    activity TEXT,
    address TEXT,
    geom GEOMETRY(Point, 4326)
);

-- Events – Que Faire à Paris
DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id UUID PRIMARY KEY,
    title TEXT,
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    geom GEOMETRY(Point, 4326)
);

-- ZTI Zones  – High Footfall Tourist Areas
DROP TABLE IF EXISTS zti_zones;
CREATE TABLE zti_zones (
    id UUID PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);
