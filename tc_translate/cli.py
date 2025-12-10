import click
import sys
from .translator import TCTranslator, Translator
from .utils import list_available_options, export_terminology, get_language_mapping
from .language_codes import convert_lang_code, is_google_supported
import json

@click.group()
def main():
    """TC Translator - Terminology Controlled Translation Tool"""
    pass

@main.command()
@click.argument('text', required=False)
@click.option('--input', '-i', 'input_file', help='Input file to translate')
@click.option('--domain', '-d', required=True, help='Domain (e.g., agric, science)')
@click.option('--target', '-t', 'target_lang', required=True, help='Target language (e.g., twi or ak)')
@click.option('--src', '-s', default='en', help='Source language (default: en)')
@click.option('--output', '-o', help='Output file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--show-codes', is_flag=True, help='Show language code information')
def translate(text, input_file, domain, target_lang, src, output, verbose, show_codes):
    """Translate text with terminology control."""
    
    if show_codes:
        src_info = get_language_mapping(src)
        target_info = get_language_mapping(target_lang)
        click.echo("Language Code Information:")
        click.echo(f"  Source: {src} → Google: {src_info['google_code']}")
        click.echo(f"  Target: {target_lang} → Google: {target_info['google_code']}")
        click.echo()
    
    # Check if target language is supported by Google
    if not is_google_supported(target_lang):
        google_code = convert_lang_code(target_lang, to_google=True)
        click.echo(f"Warning: Language '{target_lang}' may not be fully supported by Google Translate.")
        click.echo(f"  Using code '{google_code}' for translation.")
        click.echo(f"  If translation fails, try using the Google code '{google_code}' directly.")
        click.echo()
    
    # Read input
    if input_file:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            click.echo(f"Error reading input file: {e}", err=True)
            sys.exit(1)
    elif not text:
        # Read from stdin
        text = sys.stdin.read().strip()
    
    if not text:
        click.echo("No text provided", err=True)
        sys.exit(1)
    
    try:
        # Initialize translator
        translator = TCTranslator(
            domain=domain,
            target_lang=target_lang,
            src_lang=src
        )
        
        # Translate
        result = translator.translate(text)
        
        # Output result
        if verbose:
            output_data = {
                'original': result['original'],
                'translation': result['text'],
                'domain': result['domain'],
                'source_language': {
                    'input': result['src'],
                    'google_code': result['src_google']
                },
                'target_language': {
                    'input': result['dest'],
                    'original_from_terminology': result['original_dest'],
                    'google_code': result['dest_google']
                },
                'preprocessed_text': result['preprocessed'],
                'google_translation': result['google_translation'],
                'terms_replaced': result['replacements_count']
            }
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)
        else:
            output_text = result['text']
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            click.echo(f"Translation saved to {output}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--format', '-f', type=click.Choice(['json', 'text', 'detailed']), default='text')
@click.option('--code-format', type=click.Choice(['original', 'google', 'both']), default='both')
def list(format, code_format):
    """List available domains and languages."""
    try:
        options = list_available_options(format=code_format)
        
        if format == 'json':
            click.echo(json.dumps(options, indent=2))
        else:
            if code_format == 'both' or code_format == 'detailed':
                click.echo("Available Domains and Languages:")
                click.echo("=" * 60)
                
                for domain in options['domains']:
                    click.echo(f"\n{domain}:")
                    if 'domains_with_languages_original' in options:
                        orig_langs = options['domains_with_languages_original'].get(domain, [])
                        google_langs = options['domains_with_languages_google'].get(domain, [])
                        for orig, google in zip(orig_langs, google_langs):
                            click.echo(f"  - {orig} (Google: {google})")
                    else:
                        for lang in options['domains_with_languages'].get(domain, []):
                            click.echo(f"  - {lang}")
                
                if 'language_mapping' in options:
                    click.echo(f"\nLanguage Code Mapping:")
                    for orig, google in options['language_mapping'].items():
                        click.echo(f"  {orig} → {google}")
                
                click.echo(f"\nTotal: {len(options['domains'])} domains")
                
            else:
                click.echo(f"Available Domains and Languages ({options.get('language_format', '')}):")
                click.echo("=" * 40)
                
                for domain, langs in options['domains_with_languages'].items():
                    click.echo(f"\n{domain}:")
                    for lang in langs:
                        click.echo(f"  - {lang}")
                
                click.echo(f"\nTotal: {len(options['domains'])} domains, "
                          f"{len(options['languages'])} languages")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('domain')
@click.argument('language')
@click.option('--format', type=click.Choice(['json', 'csv']), default='json')
def export(domain, language, format):
    """Export terminology for a domain and language."""
    try:
        result = export_terminology(domain, language, format)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('language')
def langinfo(language):
    """Get information about a language code."""
    try:
        info = get_language_mapping(language)
        click.echo(json.dumps(info, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('filepath')
def validate(filepath):
    """Validate a terminology CSV file."""
    from .utils import validate_terminology_file
    is_valid, message = validate_terminology_file(filepath)
    
    if is_valid:
        click.echo(f"✓ {filepath} is valid")
    else:
        click.echo(f"✗ {filepath} is invalid: {message}", err=True)
        sys.exit(1)
