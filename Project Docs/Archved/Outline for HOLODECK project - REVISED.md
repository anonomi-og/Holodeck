# HOLODECK Project Outline

## Overview

Create an AI Agent that functions as a personal AI Dungeon Master for voice-based D&D gameplay. The system will run on a laptop for development and testing, with the option to run on a Raspberry Pi in production.

## Core Technology & APIs

- **Primary AI Provider:** OpenAI (have existing API key)
- **Voice Input:** OpenAI Whisper API
- **Voice Output:** Text-to-speech conversion
- **External APIs:** Encouraged for simplification over local models

## User Interaction Model

**Voice-Based Interface:**
- System continuously listens for a player name keyword (stored as a variable)
- When detected, the player name + spoken command is sent to the AI for processing
- Example: "Kraven, wants to open that door"
- AI responds with voice output

## Core Architecture

### AI Agent System
- Central AI agent or multi-agent network
- Manages narrative flow and game logic
- Processes player actions and determines outcomes

### Game Tools & Functions

| Tool | Purpose |
|------|---------|
| **Dice Roller** | Generate required dice rolls for game mechanics |
| **Room Describer** | Retrieve detailed information about specific dungeon rooms |
| **Character Sheet Reader** | Access player stats from Google Sheets (HP, items, skill values) |
| **Character Sheet Updater** | Modify character data (reduce HP, update gold, etc.) |
| **Rules Lookup** | Access simplified SRD rules for checks and actions |
| **Monster Stat Retriever** | Fetch enemy stats from database by name |

## Game Content

### Dungeon Structure
- **MVP Scope:** One 5-room dungeon
- **Storage:** Simple database
- **Accessibility:** Room overview always available; detailed descriptions accessible via Room Describer tool

### Character Management
- **Storage:** Google Sheets (simple table format)
- **Tracked Data:** HP, gold, items, skills, checks, and other key attributes
- **Updates:** Agent can read and modify values as needed for gameplay

### Rules System
- **Source:** D&D 5e SRD
- **Format:** Condensed into logical, AI-friendly instructions
- **Storage Options:** 
  - Embed in core system prompt, OR
  - Store in categorized database with lookup tool
- **Access:** Agent queries specific rules as needed

### Monsters & Enemies
- **Source:** D&D 5e SRD
- **Storage:** Database of monster stat blocks
- **Access:** Tool to retrieve stats by name

## AI Memory & Context

- **Recent Context:** Last 10 turns of gameplay
- **Key Events:** Dedicated memory store for significant narrative moments
- **Purpose:** Provide continuity and context for narrative responses

## Response Format

Agent generates structured JSON responses containing:

**Narration:** Descriptive DM text in response to player action
- Example: "You fail to persuade the guard. He demands 5 gold pieces as payment."

**Instructions:** Commands to update game state
- Format: `[reduce_gold 5]`, `[reduce_hp 3]`, `[update_location "Room 2"]`
- Targets: Character sheets, inventory, location, status effects

## Development Path

1. Set up voice I/O with Whisper API
2. Implement core AI agent with basic rules engine
3. Create database structure for dungeon, rules, and monsters
4. Build character sheet integration with Google Sheets
5. Develop tool suite for game mechanics
6. Implement memory and context management
7. Refine response generation and JSON formatting
8. Test on laptop environment
9. Optimize for Raspberry Pi deployment
