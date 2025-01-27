import os
from flask import Flask, render_template
from azure.appconfiguration.provider import load_provider, AzureAppConfigurationKeyVaultOptions, SettingSelector
from azure.identity import DefaultAzureCredential

app = Flask(__name__)


ENDPOINT =  os.environ.get("AZURE_APPCONFIG_ENDPOINT")

# Set up credentials and settings used in resolving key vault references.
credential = DefaultAzureCredential()

# Load app configuration key-values and resolved key vault reference values.
# Select only key-values that start with 'testapp_settings_' and trim the prefix
selects = SettingSelector(key_filter="testapp_settings_*")
keyvault_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
azure_app_config = load_provider(endpoint=ENDPOINT,
                                 key_vault_options=keyvault_options,
                                 credential=credential,
                                 selects=[selects],
                                 trimmed_key_prefixes=["testapp_settings_"])

# App Configuration provider implements the Mapping Type which is compatible with the existing Flask config.
# Update Flask config mapping with loaded values in the App Configuration provider.
app.config.update(azure_app_config)

@app.route('/')
def index():
   print('Request for index page received')
   context = {}
   context['message'] = app.config.get('message')
   context['font_size'] = app.config.get('font_size')
   context['color'] = app.config.get('color')
   context['key'] = app.config.get('secret_key') # This is a key vault reference. The corresponding secret in key vault is returned.
   return render_template('index.html', **context)


if __name__ == '__main__':
   app.run()
