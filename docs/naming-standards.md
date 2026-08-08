# Naming Standards

- Packages: `lowercase_with_underscores`, singular domain nouns
  (`quantum`, not `quantums`)
- Classes: `PascalCase`, nouns from the foundation ontology where
  applicable (`Entity`, `System`, `State`)
- Functions/methods: `snake_case`, verbs (`describe`, `evolve`, `observe`)
- Abstract base classes are not suffixed `Base` or `Abstract` — the
  ontology name itself is the contract (`Entity`, not `AbstractEntity`)
- Exceptions: suffixed `Error` (`ProviderUnavailableError`)
