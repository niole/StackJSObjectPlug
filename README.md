# Installation

* install python
* install python neovim
* clone this repo into `.config/nvim/`
* reference it in your `.vimrc` as `StackJSObjectPlug/stackobject.py`
* Next time you use nvim, make sure to call `:UpdateRemotePlugins`
* use the plugin

# Usage

When your cursor is on a line with the object that you want to 'stack', execute `:Sobj`. This plugin will rewrite the object.

a rewrite will look like the following...
```
const x = { x: 1, y: 2, };
```

result:
```
const x = {
  x: 1,
  y: 2,
};
