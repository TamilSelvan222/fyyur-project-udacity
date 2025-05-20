-- sample_data.sql

-- Insert into Venue
INSERT INTO venues (
    name, city, state, address, phone, genres,
    image_link, facebook_link, website_link,
    seeking_talent, seeking_description, created_at
) VALUES (
    'The Musical Hop', 
    'San Francisco', 
    'CA', 
    '1015 Folsom Street', 
    '123-123-1234',
    ARRAY['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk'],
    'https://images.unsplash.com/photo-1543900694-133f37abaaa5',
    'https://www.facebook.com/TheMusicalHop',
    'https://www.themusicalhop.com',
    TRUE, 
    'We are on the lookout for a local artist to play every two weeks. Please call us.',
    NOW()
);

-- Insert into Artist
INSERT INTO artists (
    name, city, state, phone, genres,
    website_link, image_link, facebook_link,
    seeking_venue, seeking_description, availability, created_at
) VALUES (
    'Guns N Petals', 
    'San Francisco', 
    'CA', 
    '326-123-5000',
    ARRAY['Rock n Roll'],
    'https://www.gunsnpetalsband.com',
    'https://images.unsplash.com/photo-1549213783-8284d0336c83',
    'https://www.facebook.com/GunsNPetals',
    TRUE,
    'Looking for shows to perform at in the San Francisco Bay Area!',
    '{"mon": "10:00-18:00", "tue": "10:00-18:00"}',
    NOW()
);

-- Insert into Show
INSERT INTO shows (
    artist_id, venue_id, start_time
) VALUES (
    1, 1, '2025-06-15 21:00:00'
);
