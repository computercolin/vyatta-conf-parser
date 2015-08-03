# coding:utf-8
import unittest
import re
import sys
import datadiff
from datadiff.tools import assert_equal

import vyattaconfparser as vparser

class TestBackupOspfRoutesEdgemax(unittest.TestCase):        
    def test_basic_parse_works_a1(self, dos_line_endings=False):
        s = """interfaces {
             ethernet eth0 {
                 address 192.168.0.2/24
                 address 192.168.1.2/24
                 description eth0-upstream
                 duplex auto
                 speed auto
             }
             ethernet eth1 {
                 address 192.168.2.2/24
                 description eth1-other
                 duplex auto
                 speed auto
             }"""
        if dos_line_endings:
          s = s.replace('\n', '\r\n')
        correct = {
          'interfaces': {
            'ethernet': {
              'eth0': {
                'address': ['192.168.0.2/24', '192.168.1.2/24'],
                'description': 'eth0-upstream',
                 'duplex': 'auto',
                 'speed': 'auto'
              },
              'eth1': {
                'address': '192.168.2.2/24',
                'description': 'eth1-other',
                 'duplex': 'auto',
                 'speed': 'auto'
              }
            }
          }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict) 
        assert_equal(rv, correct)

    def test_basic_parse_works_a1_dos_endings(self):
        self.test_basic_parse_works_a1(dos_line_endings=True)

    def test_parsing_quoted_config_vals(self):
        s = """interfaces {
             ethernet eth0 {
                 description "eth0-upstream 302.5-19a"
                 duplex auto
                 speed auto
             }
        }"""
        correct = {
          'interfaces': {
            'ethernet': {
              'eth0': {
                'description': 'eth0-upstream 302.5-19a',
                 'duplex': 'auto',
                 'speed': 'auto'
              }
            }
          }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict) 
        assert_equal(rv, correct)

    def test_parsing_quoted_config_vals_special_chars(self):
        s = """interfaces {
             ethernet eth0 {
                 description "eth0-upstream #302.5-19a (temp path)"
                 duplex auto
                 speed auto
             }
        }"""
        correct = {
          'interfaces': {
            'ethernet': {
              'eth0': {
                'description': 'eth0-upstream #302.5-19a (temp path)',
                 'duplex': 'auto',
                 'speed': 'auto'
              }
            }
          }
        }
        rv = vparser.parse_conf(s)
        assert isinstance(rv, dict) 
        assert_equal(rv, correct)

    def test_detailed_config_parse_correctly_a1(self):
      s, correct = get_detailed_parse_str_dict()
      rv = vparser.parse_conf(s)
      assert isinstance(rv, dict) 
      assert_equal(rv, correct)
      


    ## Future comment parsing (using '_comment' key -- parsed obj format not yet selected).
    # def test_parsing_config_comments(self):
    #     s = """interfaces {
    #          ethernet eth0 {
    #              /* temp subnet -- chars NORMAL */
    #              address 192.168.0.2/24
    #              address 192.168.1.2/24
    #              duplex auto
    #              speed auto
    #          }
    #     }"""
    #     correct = {
    #       'interfaces': {
    #         'ethernet': {
    #           'eth0': {
    #              'address': {
    #                '192.168.0.2/24': {'_comment': 'temp subnet -- chars NORMAL'},
    #                '192.168.1.2/24': {}
    #              },
    #              'duplex': 'auto',
    #              'speed': 'auto'
    #           }
    #         }
    #       }
    #     }
    #     rv = vparser.parse_conf(s)
    #     assert isinstance(rv, dict) 
    #     assert_equal(rv, correct)
    #
    # def test_parsing_config_comments_special_chars(self):
    #     s = """interfaces {
    #          ethernet eth0 {
    #              /* temp subnet -- chars Sw #23 (temp 2.3.9) */
    #              address 192.168.0.2/24
    #              address 192.168.1.2/24
    #              duplex auto
    #              speed auto
    #          }
    #     }"""
    #     correct = {
    #       'interfaces': {
    #         'ethernet': {
    #           'eth0': {
    #              'address': {
    #                '192.168.0.2/24': {'_comment': 'temp subnet -- chars Sw #23 (temp 2.3.9)'},
    #                '192.168.1.2/24': {}
    #              },
    #              'duplex': 'auto',
    #              'speed': 'auto'
    #           }
    #         }
    #       }
    #     }
    #     rv = vparser.parse_conf(s)
    #     assert isinstance(rv, dict) 
    #     assert_equal(rv, correct)


def get_detailed_parse_str_dict():
  s = """
    interfaces {
       ethernet eth0 {
           address 192.168.0.2/24
           address 192.168.1.2/24
           description eth0-upstream
           duplex auto
           ip {
               ospf {
                   authentication {
                       md5 {
                           key-id 1 {
                               md5-key 1234567890
                           }
                       }
                   }
                   cost 2
                   dead-interval 40
                   hello-interval 10
                   priority 1
                   retransmit-interval 5
                   transmit-delay 1
               }
           }
           speed auto
       }
       ethernet eth1 {
           address 192.168.2.2/24
           description eth1-other
           duplex auto
           speed auto
       }
    }
    protocols {
        static {
            route 0.0.0.0/0 {
                next-hop 1.2.3.4 {
                    distance 10
                }
            }
            route 10.1.0.5/32 {
                next-hop 2.3.4.5 {
                    distance 180
                }
            }
            route 10.2.0.0/24 {
                next-hop 1.2.3.4 {
                    distance 180
                }
            }
            route 10.3.1.0/24 {
                next-hop 44.55.3.2 {
                    distance 180
                }
            }
      }
    }
    """
  correct = {
    'interfaces': {
      'ethernet': {
        'eth0': {
          'address': ['192.168.0.2/24', '192.168.1.2/24'],
          'description': 'eth0-upstream',
          'duplex': 'auto',
          'speed': 'auto',
          'ip': {
            'ospf': {
              'authentication': {
                'md5': {
                  'key-id': {
                    '1': {'md5-key': '1234567890'}
                  }
                }
              },
              'cost': '2',
              'dead-interval': '40',
              'hello-interval': '10',
              'priority': '1',
              'retransmit-interval': '5',
              'transmit-delay': '1'
            }
          }
        },
        'eth1': {
          'address': '192.168.2.2/24',
          'description': 'eth1-other',
           'duplex': 'auto',
           'speed': 'auto'
        }
      }
    },
    'protocols': {
      'static': {
        'route': {
          '0.0.0.0/0': {
            'next-hop': {'1.2.3.4': {'distance': '10'}}
          },
          '10.1.0.5/32': {
            'next-hop': {'2.3.4.5': {'distance': '180'}}
          },
          '10.2.0.0/24': {
              'next-hop': {'1.2.3.4': {'distance': '180'}}
          },
          '10.3.1.0/24': {
              'next-hop': {'44.55.3.2': {'distance': '180'}}
          }
        }
      }
    }




  }
  return (s, correct)

if __name__ == "__main__":
    unittest.main()
