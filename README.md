<p align="center">
      <img src="https://i.ibb.co/0XcwvjC/photo.jpg" alt="PetProjectPhoto" border="0" width="727">
</p>

<p align="center">
   <img alt="Static Badge" src="https://img.shields.io/badge/Licencse-MIT-success">
   <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/vk-api">
   <img alt="Poetry badge" src="https://img.shields.io/badge/packaging-poetry-cyan.svg">
</p>

## About

The bot is for the VK platform, it doesn't have too many functions, but still they are there, and as a template for large projects, you can use such a structure, you can see too much nesting in the code, but the library itself implies it.

<h3>Main functions: </h3>
<ul>
<li>Getting the weather by city name</li>
<li>Getting information from Wiki request</li>
<li>Receiving, deleting, and recording notes</li>
<li>Getting an interesting fact about the number</li>
<li>Sending messages to users from the admin</li>
</ul>

## Documentation

<h3>Base settings</h3>
<ol>
<li>Download the project from github</li>
<li>Use the console to navigate to the copied repository</li>
<li>Install dependencies from the requirements file with the command: pip install -r requirements.txt</li>
<ul>
<li>Or through a file pyproject.toml , being in the same directory as the file, enter: poetry install</li>
<li>After that, you will have a virtual environment with all the dependencies, enter this environment with the command: poetry shell</li>
</ul>
<li>Create and configure the file .env when using the file .env_example</li>
</ol>

<h3>Launching the application</h3>
<ol>
<li>After setting up the environment, you can launch the application</li>
<li>Go to the /app directory via the terminal and enter the command: python main.py</li>
      <ul>
            <li>Or run the application through poetry with the command: poetry run python main.py</li>
      </ul>
<li>Now the bot should be running, logging is enabled.</li>
<li>Go to your group for which you created the bot token, and write /start in your personal messages to launch the bot.</li>
</ol>

<h3>After writing to the bot, you should see the following text:</h3>
<img src="https://i.ibb.co/bbmR6ys/start.jpg" alt="start message" border="0" width="300" height="500">


## Distribute

## Developers

- [DarkPythons](https://github.com/DarkPythons)

## License
The VkBot project is distributed under the MIT license.

## Examples of dialogue with a bot
<p>
      <img src="https://i.ibb.co/LpZ5zQJ/fakt.jpg" alt="fakt" border="0" width="300" height="450">
      <img src="https://i.ibb.co/jgDKzPJ/weather.jpg" alt="weather" border="0" width="300" height="450">
      <img src="https://i.ibb.co/sF5CR0Z/notes.jpg" alt="notes" border="0" width="280" height="450">
</p>
