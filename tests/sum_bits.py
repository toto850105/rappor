#!/usr/bin/python
#
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Read the output of the RAPPOR simulation, and sum the bits by cohort to produce
a Counting Bloom filter.  This can then be analyzed by R.
"""

import csv
import sys


class Error(Exception):
  pass


# Update rappor sum
def update_rappor_sums(rappor_sum, rappor, cohort, params):
  for bit_num in xrange(params.num_bloombits):
    if rappor & (1 << bit_num):
      rappor_sum[cohort][1 + bit_num] += 1
  rappor_sum[cohort][0] += 1  # The 0^th entry contains total reports in cohort

def dummy():
  # Print sums of all rappor bits into output file
  with open(inst.outfile, 'w') as f:
    for row in xrange(params.num_cohorts):
      for col in xrange(params.num_bloombits):
        f.write(str(rappor_sums[row][col]) + ",")
      f.write(str(rappor_sums[row][params.num_bloombits]) + "\n")

  # Initializing array to capture sums of rappors.
  rappor_sums = [[0] * (params.num_bloombits + 1)
                 for _ in xrange(params.num_cohorts)]

      # Sum rappors.  TODO: move this to separate tool.
  rappor.update_rappor_sums(rappor_sums, r, cohort, params)
  return rappor_sums

class Foo:
  def testUpdateRapporSumsWithLessThan32BitBloomFilter(self):
    report = 0x1d  # From LSB, bits 1, 3, 4, 5 are set
    # Empty rappor_sum
    rappor_sum = [[0] * (self.typical_instance.num_bloombits + 1)
                  for _ in xrange(self.typical_instance.num_cohorts)]
    # A random cohort number
    cohort = 42

    # Setting up expected rappor sum
    expected_rappor_sum = [[0] * (self.typical_instance.num_bloombits + 1)
                           for _ in xrange(self.typical_instance.num_cohorts)]
    expected_rappor_sum[42][0] = 1
    expected_rappor_sum[42][1] = 1
    expected_rappor_sum[42][3] = 1
    expected_rappor_sum[42][4] = 1
    expected_rappor_sum[42][5] = 1

    rappor.update_rappor_sums(rappor_sum, report, cohort,
                              self.typical_instance)
    self.assertEquals(expected_rappor_sum, rappor_sum)







def main(argv):
  """Returns an exit code."""
  # TODO: need to read params file?
  num_cohorts = 64
  num_bloombits = 16
  sums = [[0] * num_bloombits for _ in xrange(num_cohorts)]
  num_reports = [0] * num_cohorts

  csv_in = csv.reader(sys.stdin)
  for i, (user_id, cohort, irr) in enumerate(csv_in):
    if i == 0:
      continue  # skip header

    cohort = int(cohort)
    num_reports[cohort] += 1

    #print repr(irr)
    assert len(irr) == 16, len(irr)
    for i, c in enumerate(irr):
      bit_num = num_bloombits - i - 1  # e.g. char 0 = bit 15, char 15 = bit 0
      if c == '1':
        sums[cohort][bit_num] += 1
      else:
        if c != '0':
          raise Error('Invalid IRR -- digits should be 0 or 1')
    #print line

  for cohort in xrange(num_cohorts):
    # First column is the total number of reports in the cohort.
    row = [num_reports[cohort]] + sums[cohort]
    print ','.join(str(cell) for cell in row)

  return 0


if __name__ == '__main__':
  try:
    sys.exit(main(sys.argv))
  except Error, e:
    print >> sys.stderr, e.args[0]
    sys.exit(1)
