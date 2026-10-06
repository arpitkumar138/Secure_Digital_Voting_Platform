# Secure Digital Voting Platform 2.0

A web-based digital voting system developed using Flask and SQLite. The project demonstrates voter verification, OTP-based authentication, one-vote-per-voter protection, anonymous vote storage, and an admin results dashboard.

> **Note:** This is an educational/demo project and is not intended for real-world government elections.

## Features

- Voter ID verification
- OTP verification using Twilio Verify
- One-vote-per-voter protection
- Anonymous vote storage
- SQLite database
- Admin login
- Election results dashboard
- Session-based authentication
- Duplicate voting prevention
- Simple and user-friendly web interface

## Project Workflow

```text
Voter ID
   ↓
Voter Verification
   ↓
Twilio OTP
   ↓
OTP Verification
   ↓
Candidate Selection
   ↓
Vote Submission
   ↓
Anonymous Vote Storage
   ↓
Results Dashboard
