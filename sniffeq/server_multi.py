import os
import sys
import logging
import argparse
import linecache
import itertools
import multiprocessing

from mongoengine import connect

from sniffeq.models.submission import Submission
from sniffeq.models.number import Number
from sniffeq.models.tag import Tag
from sniffeq.models.presentation import Presentation


log = multiprocessing.log_to_stderr()
log.setLevel(logging.INFO)


class SniffEqMapper(object):
    
    def __init__(self, process_line, num_workers=None):
        self.fileToClassMap = {
            'sub.txt': Submission,
            'num.txt': Number,
            'tag.txt': Tag,
            'pre.txt': Presentation,
        }
        self.filesList = ['sub.txt', 'tag.txt', 'num.txt', 'pre.txt']

        self.process_line = process_line
        self.pool = multiprocessing.Pool(num_workers)

    def __call__(self, year, quarter, chunksize=1):
        responses = {}

        for filename in self.filesList:
            path = os.path.dirname(os.path.abspath(__file__))
            filepath = '%s/data/%sq%s/%s' % (path, year, quarter, filename)
            classRef = self.fileToClassMap.get(filename)

            lines = linecache.getlines(filepath)

            index = 1
            # skip some rows
            # if classRef == Number:
            #     index = 328000

            totalNumberOfLines = len(lines)
            response = self.pool.map(
                self.process_line,
                itertools.izip(
                    itertools.repeat(classRef),
                    xrange(index, totalNumberOfLines + 100), # +100 threshold
                    itertools.repeat(totalNumberOfLines),
                    itertools.repeat(lines[0]),
                    lines[index:],
                ),
                chunksize=chunksize,
            )
            linecache.clearcache()

            success = response.count({'success': True})
            responses[filename] = {
                'success': success,
                'errors': totalNumberOfLines - index - success
            }

            log.info('Done %s!', filepath)

        return responses


def process_line(lines):
    classRef, index, total, header, row = lines
    header = header.strip().split('\t')
    row = row.strip().split('\t')

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
        sys.stdout.write('\r[%s/%s] %s with key %s' % (index, total, classRef.__name__, key))
        sys.stdout.flush()
    except Exception as e:
        log.error([obj, e])
        return {'success': False, 'key': key, 'obj': obj, 'error': e}

    # don't continue if object is not Number or Presentation
    if not isinstance(objRef, (Number, Presentation)):
        return {'success': True}

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
    return {'success': True}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sniff Equities Data Processor')
    parser.add_argument('-y', '--year', type=int, required=True, help='Year')
    parser.add_argument('-q', '--quarter', type=int, required=True, help='Quarter')
    parser.add_argument('-p', '--processes', type=int, default=None, help='Quarter')
    args = parser.parse_args()

    # start processing data
    mapper = SniffEqMapper(process_line, num_workers=args.processes)
    responses = mapper(args.year, args.quarter)
    log.info('Done %sq%s!', args.year, args.quarter)
    log.info(responses)
