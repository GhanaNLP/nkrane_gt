import click
import sys
from .translator import TCTranslator, Translator
from .utils import list_available_options, export_terminology
import json

@click.group()
def main():
    """TC Translator - Terminology Controlled Translation Tool"""
    pass

@main.command()
@click.argument('text', required=False)
@click.option('--input', '-i', 'input_file', help='Input file to translate')
@click.option('--domain', '-d', required=True, help='Domain (e.g., agric, science)')
@click.option('--target', '-t', 'target_lang', required=True, help='Target language (e.g., twi)')
@click.option('--src', '-s', default='en', help='Source language (default: en)')
@click.option('--output', '-o', help='Output file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def translate(text, input_file, domain, target_lang, src, output, verbose):
    """Translate text with terminology control."""
    
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
                'source_language': result['src'],
                'target_language': result['dest'],
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
@click.option('--format', '-f', type=click.Choice(['json', 'text']), default='text')
def list(format):
    """List available domains and languages."""
    try:
        options = list_available_options()
        
        if format == 'json':
            click.echo(json.dumps(options, indent=2))
        else:
            click.echo("Available Domains and Languages:")
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

if __name__ == '__main__':
    main()
