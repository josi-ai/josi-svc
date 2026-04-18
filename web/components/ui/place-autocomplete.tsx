'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface PlaceAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (place: { name: string; lat: number; lng: number }) => void;
  placeholder?: string;
  className?: string;
  style?: React.CSSProperties;
}

declare global {
  interface Window {
    google?: typeof google;
    _googleMapsLoaded?: boolean;
    _googleMapsCallbacks?: (() => void)[];
  }
}

function loadGoogleMaps(): Promise<void> {
  return new Promise((resolve) => {
    if (window._googleMapsLoaded && window.google?.maps?.places) {
      resolve();
      return;
    }

    if (window._googleMapsCallbacks) {
      window._googleMapsCallbacks.push(() => resolve());
      return;
    }

    window._googleMapsCallbacks = [() => resolve()];

    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    if (!apiKey) {
      console.warn('Google Maps API key not set');
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      window._googleMapsLoaded = true;
      window._googleMapsCallbacks?.forEach((cb) => cb());
      window._googleMapsCallbacks = undefined;
    };
    document.head.appendChild(script);
  });
}

export default function PlaceAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = 'City, Country',
  className = '',
  style,
}: PlaceAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const [loaded, setLoaded] = useState(false);

  // Keep refs to latest callbacks so the Google Maps listener never goes stale
  const onChangeRef = useRef(onChange);
  const onSelectRef = useRef(onSelect);
  onChangeRef.current = onChange;
  onSelectRef.current = onSelect;

  useEffect(() => {
    loadGoogleMaps().then(() => setLoaded(true));
  }, []);

  useEffect(() => {
    if (!loaded || !inputRef.current || autocompleteRef.current) return;

    const autocomplete = new google.maps.places.Autocomplete(inputRef.current, {
      types: ['(cities)'],
    });

    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      if (place.formatted_address) {
        onChangeRef.current(place.formatted_address);
        if (onSelectRef.current && place.geometry?.location) {
          onSelectRef.current({
            name: place.formatted_address,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
          });
        }
      } else if (place.name) {
        onChangeRef.current(place.name);
      }
    });

    autocompleteRef.current = autocomplete;
  }, [loaded]);

  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={className}
      style={style}
      autoComplete="off"
    />
  );
}
