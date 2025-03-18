#!/usr/bin/env python3
# encoding: utf-8

import sys
import argparse
from workflow import Workflow
import webbrowser

def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Amazon product URL to open')
    args = parser.parse_args(wf.args)

    # Open the URL in the default browser
    webbrowser.open(args.url)
    
    return 0

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main)) 