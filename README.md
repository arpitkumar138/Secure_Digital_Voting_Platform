# Secure Digital Voting Platform

A web-based digital voting platform built with Flask and SQLite that provides voter verification, one-vote-per-voter protection, vote storage, admin result management, and SMS confirmation using Twilio.

## Features

- Voter ID verification
- One voter can vote only once
- Secure vote storage using SQLite
- Admin login
- Election results dashboard
- SMS confirmation after successful voting
- Session-based authentication
- Basic error handling
- Simple and user-friendly web interface

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- Twilio API

## Project Workflow

1. Voter enters their Voter ID.
2. System verifies the voter from the database.
3. System checks whether the voter has already voted.
4. Eligible voter selects a candidate.
5. Vote is stored in the SQLite database.
6. Voter status is updated to prevent duplicate voting.
7. SMS confirmation is sent through Twilio.
8. Admin can log in and view election results.

## Database

The project uses SQLite with two main tables:

### voters

Stores:

- Voter ID
- Mobile number
- Voting status

### votes

Stores:

- Vote ID
- Voter ID
- Selected candidate/party

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Secure_Digital_Voting_Platform