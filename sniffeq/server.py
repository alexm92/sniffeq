import os
import sys
import logging
import argparse
from mongoengine import connect

from sniffeq.models.submission import Submission
from sniffeq.models.number import Number
from sniffeq.models.tag import Tag
from sniffeq.models.presentation import Presentation


log = logging.getLogger('server')

class SniffEqServer(object):
    """
    """

    def __init__(self):
        log.info('Started server!')

    def populate(self, year, quarter):
        path = os.path.dirname(os.path.abspath(__file__))
        files_to_class_map = {
            'sub.txt': Submission,
            'num.txt': Number,
            'tag.txt': Tag,
            'pre.txt': Presentation,
        }
        files_list = ['sub.txt', 'tag.txt', 'num.txt', 'pre.txt']

        for filename in files_list:
            classRef = files_to_class_map.get(filename)

            filename = '%s/data/%sq%s/%s' % (path, year, quarter, filename)
            log.info('Started processing file: %s', filename)
            with open(filename, 'r') as f:
                # count total lines in file, and move at beginning
                total_errors = 0
                total_lines = sum(1 for _ in f)
                f.seek(0)

                header = None

                # insert each row into DB 
                for index, line in enumerate(f):
                    line = line.strip().split('\t')
                    if not header:
                        header = line
                    else:
                        # skip some fields
                        if classRef == Presentation and index < 247100:
                            log.info('Skipping %s: %s...', classRef.__name__, index)
                            continue

                        row = line
                        obj = {}
                        for key, value in zip(header, row):
                            try:
                                value = value.decode('unicode-escape').encode('ascii', 'xmlcharrefreplace')
                            except:
                                pass

                            # if value is empty don't pass it
                            if not value:
                                continue

                            obj[key] = value

                        try:
                            key = obj.get('adsh', obj.get('tag'))
                            objRef = classRef(**obj).save()
                            sys.stdout.write('\r[%s/%s] %s with key %s' % (index, total_lines, classRef.__name__, key))
                            sys.stdout.flush()
                        except Exception as e:
                            total_errors += 1
                            log.error([obj, e])
                            continue

                        # don't continue if object is not Number or Presentation
                        if not isinstance(objRef, (Number, Presentation)):
                            continue

                        # get submission
                        try:
                            submissionRef = Submission.objects.get(adsh=objRef.adsh)
                            objRef.submissionRef = submissionRef
                        except Submission.DoesNotExist:
                            log.error('Submission %s DoesNotExist', objRef.adsh)
                       
                        # get tag
                        try:
                            tagRef = Tag.objects.get(tag=objRef.tag, version=objRef.version)
                            objRef.tagRef = tagRef
                        except Tag.DoesNotExist:
                            log.error('Tag (%s, %s DoesNotExist', objRef.tag, objRef.version)

                        if isinstance(objRef, Presentation):
                            # get numbers
                            numbersRef = Number.objects.filter(adsh=objRef.adsh, tag=objRef.tag, version=objRef.version)
                            objRef.numbersRef = numbersRef

                        # save
                        objRef.save()


                log.info('Done %sq%s! Got %s errors for %s...', year, quarter, total_errors, classRef.__name__)

def main():
    parser = argparse.ArgumentParser(description='Sniff Equities -- sniffeqserver')
    parser.add_argument('-y', '--year', type=int, help='Year')
    parser.add_argument('-q', '--quarter', type=int, help='Quarter')
    args = parser.parse_args()

    app = SniffEqServer()

    if args.year and args.quarter:
        log.info('Population started')
        app.populate(args.year, args.quarter)


if __name__ == '__main__':
    main()

