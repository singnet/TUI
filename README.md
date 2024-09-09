# Introduction

## Welcome

Welcome to the SingularityNET TUI documentation.&#x20;

Continue reading for some introductory information about the app, or jump right in with [getting-started](documentation/getting-started/ "mention")

Alternatively, if you would like to jump into a specific section of the documentation, take a look at the [Table of contents](documentation/TOC.md)

## What is the CLI?

The SingularityNET command line interface (CLI) is an essential tool for interacting with the SingularityNET platform, particularly its smart contracts, service management, and fund handling. This CLI is designed for both service providers and consumers, offering a comprehensive suite of commands to interface with the platform blockchain effectively.

For further information about the SingularityNET CLI, please visit the following websites:

* [Command Documentation](https://snet-cli-docs.singularitynet.io/)
* [Service Invocation Documentation](https://dev.singularitynet.io/docs/ai-consumers/invoke-service-snet-cli/)
* [GitHub](https://github.com/singnet/snet-cli)
* [PyPi Package](https://pypi.org/project/snet.cli/)

## What is the TUI?

The SingularityNET text-user-interface (TUI) is a [mouse-centric](documentation/faq/i-want-to-use-my-keyboard-instead-of-my-mouse), minimalistic text overlay for the SingularityNET CLI. The sole purpose of this application is to make interacting with the CLI, and by extension the SingularityNET platform, a little bit more user friendly (mouse/menu interaction, command parameter delineation, etc.)

<figure><img src=".gitbook/assets/Screenshot 2024-06-30 at 8.16.20 AM.png" alt=""><figcaption><p>Start Screen</p></figcaption></figure>

The TUI is structured to offer an intuitive user experience, enabling interactions primarily through a "GUI-like" experience. It constructs CLI commands from user input, then executes them in the background. Post-execution, the output is presented to the user in a clear and concise notification box. The interface is designed to be straightforward, with a persistent sidebar that allows the user quick navigation through the 5 "primary" menus.

**Key Features of the SingularityNET CLI/TUI:**

* **Account Management**: Create and manage identities for secure interactions on the platform.
* **Registry Management**: Register and manage organizations, members, services, types, and tags within the SingularityNET Registry.
* **Fund Management**: Handle customer payments using Multi-Party Escrow (MPE) and payment channels.
* **Metadata and Protobuf Management**: Read and write metadata and Protobuf specifications about AI services, stored on IPFS, with basic parameters accessible from Blockchain contracts.
* **Network Connectivity**: Connect to various networks including the Sepolia testnet, and the Ethereum mainnet.

