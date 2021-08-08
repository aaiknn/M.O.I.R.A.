#!/usr/bin/env python3

database_endpoint_not_set='MongoDB endpoint environment variables are empty meaning Moira can\'t persist anything, really.\nFunctionality will be limited.'
eonet_categories_not_set="EONET categories couldn't be set, so EONET commands can't handle any arguments. Try running another eonet self-test in order to set them."
moira_admin_and_user_not_set='Both Moira admin and Moira user permission role environment variables are empty meaning Moira can\'t assist anyone.\nYou probably wouldn\'t want that.'
openai_token_not_set='OpenAI API token environment variable is empty meaning Moira can\'t access her AI subroutines.\nFunctionality will be heavily limited.'
