#!/bin/bash

uv run exposure

#netlify deploy --dir=dist --prod
wrangler deploy
