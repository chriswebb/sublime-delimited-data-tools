# Delimited Data Tools

***[Sublime Text 3+](http://www.sublimetext.com/) Package. Install via an updated version of  [Package Control 2+](https://sublime.wbond.net/installation). Just &#42;&#42;DON'T&#42;&#42; install manually.***

## Installation

1. If you don't have it already, follow the instructions on [https://sublime.wbond.net/installation](https://sublime.wbond.net/installation) to install Package Control 2+.
2. In Sublime Text, press <kbd>Ctrl+Shift+P</kbd> (Win, Linux) or <kbd>⌘⇧p</kbd> (OS X) to open the command palette.
3. Choose `Package Control: Install Package`.
4. Select **Delimited Data Tools**.

## Description 

A plugin for Sublime Text that supplies common tools for handling delimited data.

See: http://www.sublimetext.com/


## Setup

Create a Main.sublime-menu file in your Packages/User folder. Add "default_delimter" and "default_text_identifier"

### Add a new parsing technique

To add a custom format technique to the Delimited Data menu under Tools, edit the Main.sublime-menu with the following information:

```js
[{
    "id": "tools",
    "children":
    [{
        "id":"delimited-data-tools",
        "children":
        [{
            "id": "my-custom-format",
            "caption":"Custom Format",
            "command":"delimited_format",
            "args": { "delimiter": ";", "text_identifier": "'" }
        }]
    }]
}]
```

Next click Tools > Delimited > Custom Format

## References

Commands provided by this plugin:

- `delimited_format` : `args` : `Settings`

        Use a format string to format delimited data supplied from one of the following three methods:

        - Files specified in the 'files' setting
        - Selected text of the current view
        - If no text selected, all of the text in the current view



### Settings

Values used when calling delimited_format. To overwrite default values select Preferences > Delimited Data Tools > Settings - User. Prefix all settings with the "default_" keyword.

#### Plugin Settings 

 - `output_to_newfile` : `Boolean`

        Creates a new file for each file or region which runs when the psql command is called.

 - `delimiter` : `String`

        Creates a new file for each file or region which runs when the psql command is called.

 - `text_field_identifier` : `String`

        Creates a new file for each file or region which runs when the psql command is called.

 - `files` : `[]`

        A list of files to run the format against.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License

MIT License. See LICENSE file.
