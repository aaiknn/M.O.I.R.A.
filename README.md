# M.O.I.R.A. Personal Assistant
A Discord bot that will talk to a few APIs on your behalf.

**Note**: This project is in prototype stage. A lot of things will change in the future, so it might not be advisable to use it as a dependency for one of your own just yet.
**Note**: For any issues or requests, please use the issue reporting function on the project's GitHub page.

## User Documentation
### NO_COLOR
M.O.I.R.A. will respect your preference for term colour output depending on whether or not the `NO_COLOR` environment variable is set as promoted by [no-color.org](https://no-color.org/) initiative.

### Sub-routines
Sub-routines fuel M.O.I.R.A.'s power. Without them, she'll still be there, but her helpfulness will be limited.

Sub-routines include:
* Database persistence via MongoDB (`shortname`: `DB`)
* Research capabilities via OpenAI (`shortname`: `AI`)

### Terminal and Discord Logging
There are two ways in which relevant things can be logged for two different purposes:

1. The programme will attempt to log relevant script information.
2. The programme features an event system with basic automated moderation.

Both of these types log to the terminal.
You can also opt to additionally log them to dedicated channels in Discord by setting up Webhooks in your Discord server settings. After this, the webhooks ids and tokens need to go into your `.env` file. The variable names are as follows:

```
MOIRA_WEBHOOKS_LOGS_ID
MOIRA_WEBHOOKS_LOGS_TOKEN
MOIRA_WEBHOOKS_OPEN_LOGS_ID
MOIRA_WEBHOOKS_OPEN_LOGS_TOKEN
```

The `WEBHOOKS_LOGS` variables are meant for script information, while the `WEBHOOKS_OPEN_LOGS` ones are for moderation.
If you do not wish to log anything to Discord, simply leave these blank.

### Session Permissions
#### Regular Session User Permissions
Regular user permissions for Moira can be provided by setting `MOIRA_USER_ROLE` environment variable. By assigning regular users with a role in Discord and then setting the role name here, you'll have control over who is able to interact with Moira at all. If instead you want everyone to be able to interact with Moira, simply set the variable to `@everyone`.

For some sub-routines, Moira will ask administrators for their permission before proceeding with a regular user's query.

Regular users will not be able to query for sensitive information like system state and the likes.

#### Session Administrator Permissions
Session administrator permissions for Moira can be provided by setting `MOIRA_ADMIN_ROLE` environment variable. Session administrators will have enhanced session user permissions. By assigning higher-privilege users with a role in Discord and then setting the role name here, you'll have control over who is able to interact with Moira when it comes to querying for more sensitive information like system state.

Session administrators will be able to grant Moira permission to proceed with regular users' queries for some sub-routines.

## Troubleshooting
### Troubleshooting at runtime
#### `*moira attempt db connection`
If a database connection wasn't successful during script startup or if the database becomes unreachable during runtime, this command makes it possible to connect to it manually later.

(**Note**: M.O.I.R.A. needs a working database sub-routine for this to have any effect.)

#### `*moira reset session soft | *moira reset session hard`
If for some reason M.O.I.R.A. gets stuck in busy state during runtime, session administrators can try sending one of these messages. While a `soft` reset will clear the busy state for the channel where this message is sent, `hard` reset clears the entire object. Unless there is something horribly wrong with all sessions, `soft` reset is a safe way and a good bet to troubleshoot without having to restart.

#### `*moira print system state`
This will send a direct message to the administator session user who sent this request. The message will include caught database errors (if there have been any), database meta state information, and the current state of M.O.I.R.A.'s state machine (`MISM`).

#### `*moira print db errors`
This will send a direct message to the administrator session user who sent this request. The message will include the current queue of database-related errors stored in `moira.db.errors`.

#### `*moira print db state`
This will send a direct message to the administrator session user who sent this request. The message will include the current database meta state information.

## Maintenance and Data Backup
### Graceful Shutdown
#### `*moira graceful shutdown`
If M.O.I.R.A. needs to be restarted, session administrators can send this message to save state in the database, so that all the data from state isn't lost and can be loaded into the context during the next start-up.

(**Note**: M.O.I.R.A. needs a working database sub-routine for this to have any effect.)

### Retrieving and Restoring State
#### `*moira load last state`
This will retrieve M.O.I.R.A.'s last gracefully stored state from the database and then load it into runtime state.
It is advised to do this right after startup in order to prevent overriding the current session state.

(**Note**: M.O.I.R.A. needs a working database sub-routine for this to have any effect.)

## Dev Documentation
### Discord Webhook Logs Default Colour Scheme
[Paletton Scheme](https://paletton.com/#uid=7021N0koZxE2FFEfmCbDxucSnns)
