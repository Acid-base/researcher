# SearXNG Configuration Directory

This directory contains configuration files for the SearXNG search engine.

## About SearXNG

SearXNG is a privacy-respecting, hackable metasearch engine that aggregates results from various search engines without storing user information.

## Configuration

When the docker-compose stack is started, this directory will be mounted into the SearXNG container at `/etc/searxng`.

You can customize SearXNG by adding a `settings.yml` file in this directory. For example:

```yaml
# settings.yml example
general:
  debug: false
  instance_name: "Deep Research Tool"

search:
  safe_search: 0
  autocomplete: "google"

server:
  bind_address: "0.0.0.0"
  port: 8080

ui:
  theme_args:
    simple_style: auto
```

See the [SearXNG documentation](https://searxng.github.io/searxng/admin/settings.html) for all available settings.

## Search Engines

SearXNG aggregates results from numerous search engines including Google, Bing, DuckDuckGo, and many specialized engines.

By default, this implementation uses a balanced selection of search engines, but you can customize which ones are enabled in the settings.yml file.
